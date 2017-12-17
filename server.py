from flask import Flask, request, redirect, render_template, session, flash
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Cat
from daily import *
from helper_functions import *
from pytz import timezone
import pytz
import random
import bcrypt
from functools import partial
import os
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# import time 
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
################################################################################
scheduler = BackgroundScheduler()
scheduler.start()

US_TIMEZONES = ['US/Pacific', 'US/Eastern', 'US/Alaska', 'US/Arizona',
                'US/Central','US/Hawaii','US/Mountain',]


@app.route("/")
def main():
    """Render main page"""

    return render_template("home.html")

@app.route('/email_exists.json')
def get_email_existence():
    """Check if an email is valid, send data back to page"""

    email = request.args.get("email")

    if User.query.filter_by(email=email).first():
        return ""
    else:
        return "Email not in database. Register or try again."

@app.route('/password_correctness.json')
def check_password():
    """Check if user's password is correct, send data back to page"""

    # it's a bit redundant to check on the front AND back end ... need to think about this

    email = request.args.get("email")
    password = request.args.get("password")
    password = password.encode('utf-8')

    existing_email = User.query.filter_by(email=email).first()

    user = User.query.filter_by(email=email).first()
    if user:
        hashed = user.password
        hashed = hashed.encode('utf-8')

    if existing_email is not None and bcrypt.checkpw(password, hashed):
        return ""
    else:
        return "Incorrect password."


@app.route("/login", methods=["POST"])
def login():
    """Attempt to log the user in"""

    email = request.form.get("email")
    password = request.form.get("password")
    password = password.encode('utf-8')

    existing_email = User.query.filter_by(email=email).first()

    user = User.query.filter_by(email=email).first()

    if user:
        hashed = user.password
        hashed = hashed.encode('utf-8')

    if (existing_email is not None and 
        bcrypt.checkpw(password, hashed) and 
        user.is_verified == True):
        # add user to session
        session["user_id"] = existing_email.user_id
        user_id = session["user_id"]

        flash("Successfully logged in!")
        
        return redirect("/main") 

    elif existing_email is None:
        flash("Incorrect email.")
        return redirect('/')
    elif user.is_verified == False:
        flash("Number not verified.")
        return redirect('/')
    else:
        flash("Incorrect password.")
        return redirect('/')

@app.route("/logout")
def do_logout():
    """Log user out."""

    flash("Goodbye!")
    session["user_id"] = ""

    return redirect("/")

@app.route("/register", methods=["GET"])
def register():
    """Show registration form"""

    return render_template("register.html", timezones=US_TIMEZONES)

@app.route("/register", methods=["GET", "POST"])
def register_process():
    """Get information from registration form."""

    email = request.form.get("email")

    password = request.form.get("password")
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    phone = request.form.get("phone")
    country_code = '+1' # US country code
    phone = ''.join(num for num in phone if num not in '-')
    phone = country_code + phone

    name = request.form.get('cat-name')
    dinner_time = request.form.get('dinner-time')
    ampm = request.form.get('ampm')
    timezone = request.form.get('timezone')

    time = parse_time(dinner_time)
    hour, minutes = time
    hour = make_24_hour_time(ampm, hour)
    date = convert_to_utc(hour, minutes, timezone)

    snack = request.form.get('cat-snack')
    activity1 = request.form.get('cat-activity')
    activity2 = request.form.get('cat-activity2')
    toy1 = request.form.get('cat-toy')
    toy2 = request.form.get('cat-toy2')

    existing_email = User.query.filter_by(email=email).first()

    # check if the email is in use
    if existing_email is None:
        new_user = User(email=email, password=password, phone_number=phone,
                        timezone=timezone)
        db.session.add(new_user)
        db.session.commit()

        existing_email = User.query.filter_by(email=email).first()
        session["user_id"] = existing_email.user_id
        current_user = session["user_id"]

        new_cat = Cat(user_id=current_user, name=name, dinner_time=date, 
                  snack=snack, activity1=activity1, activity2=activity2, 
                  toy1=toy1, toy2=toy2)
        db.session.add(new_cat)
        db.session.commit()

        bound_f = partial(daily_text, name, phone)

        scheduler.add_job(
            func=bound_f,
            trigger=CronTrigger(hour=date.hour, minute=date.minute),
            id=str(current_user), # if expanding to allow for multiple cats, change this
            # name="Job for " + current_user + ". Sending text at " + date.hour + ":" + date.minute,
            replace_existing=False)


        code = ""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        while len(code) < 6:
            a_letter = random.choice(chars)
            code += a_letter

        message = client.messages.create(
        to=phone, 
        from_="+14138486585",
        # body="Hi, it's " + name + ". I like " + snack + "! Feed me at " + dinner_time + "!")
        body=code)
        print(message.sid)

        # flash("Successfully registered " + email + "!")
        return render_template("verification.html", code=code)
        # return render_template("thanks.html")

    else:
        flash("Email already in use")

    return redirect("/")

@app.route('/verification', methods=["POST"])
def verify_phone_number():
    """Mark user as verified"""

    user_id = session["user_id"]
    cat = Cat.query.filter_by(user_id=user_id).first()
    user = User.query.filter_by(user_id=user_id).first()
    user.is_verified = True

    db.session.commit()

    message = client.messages.create(
    to=user.phone_number, 
    from_="+14138486585",
    body="Hi, it's " + cat.name + ". I like " + cat.snack + "! Can't wait to text a lot!")
    print(message.sid)

    flash("Successfully registered " + user.email + "!")
    return render_template("thanks.html")


@app.route('/email_in_use')
def get_email_status():
    """Check if an email is in use or not"""

    email = request.args.get("email")

    if User.query.filter_by(email=email).first():
        return "Email is already in use"
    return ""


@app.route("/main")
def main_page():
    """Render main page"""

    user_id = session["user_id"]
    cat = Cat.query.filter_by(user_id=user_id).first()

    user_time = cat.user.timezone
    cat.dinner_time = cat.dinner_time.replace(tzinfo=pytz.utc)
    cat.dinner_time = cat.dinner_time.astimezone(timezone(user_time))

    time = [str(cat.dinner_time.hour), ":", str(cat.dinner_time.minute)]
    time = parse_time("".join(time))
    hour, minutes = time
    new_minutes = make_minutes(minutes)

    ampm = am_or_pm(hour) # get whether am or pm
    hour = make_12_hour_time(hour) # convert to 12 hour time


    return render_template("main.html", name=cat.name, toy1=cat.toy1, 
                                        toy2=cat.toy2, snack=cat.snack, 
                                        activity1=cat.activity1,
                                        activity2=cat.activity2, 
                                        ampm=ampm, hour=hour, 
                                        minutes=new_minutes)


@app.route("/update")
def show_update():
    """Show update page"""

    return render_template("update.html", timezones=US_TIMEZONES)


@app.route("/update", methods=['POST'])
def do_update():
    """Update details in db"""

    name = request.form.get('cat-name')
    dinner_time = request.form.get('dinner-time')
    ampm = request.form.get('ampm')
    timezone = request.form.get('timezone')
    snack = request.form.get('cat-snack')
    activity1 = request.form.get('cat-activity')
    activity2 = request.form.get('cat-activity2')
    toy1 = request.form.get('cat-toy')
    toy2 = request.form.get('cat-toy2')

    user_id = session["user_id"]
    cat = Cat.query.filter_by(user_id=user_id).first()

    if name:
        cat.name = name

    if dinner_time:
        time = parse_time(dinner_time)
        hour, minutes = time
        hour = make_24_hour_time(ampm, hour)
        date = convert_to_utc(hour, minutes, timezone)
        cat.dinner_time = date
        cat.dinner_time = cat.dinner_time.replace(tzinfo=None)

    if toy1:
        cat.toy1 = toy1
    if toy2:
        cat.toy2 = toy2
    if snack:
        cat.snack = snack
    if activity1:
        cat.activity1 = activity1
    if activity2:
        cat.activity2 = activity2

    db.session.commit()

    if dinner_time:
        name = cat.name
        phone_number = cat.user.phone_number

        bound_f = partial(daily_text, name, phone_number)

        scheduler.add_job(
        func=bound_f,
        trigger=CronTrigger(hour=date.hour, minute=date.minute),
        id=str(user_id), # if expanding to allow for multiple cats, change this
        replace_existing=True)

    flash("Successfully updated " + cat.name + "'s info!")

    return redirect("/main") 

def daily_text(name, phone_number):

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, " + name + " here. I'm pretty sure it's time to feed me!!")

    print(message.sid)


@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""

    phone = request.values.get('From', None)
    user_id = User.query.filter_by(phone_number=phone).first()
    cat = Cat.query.filter_by(user_id=user_id.user_id).first()

    toy1_msg = 'Can we play with my ' + cat.toy1 + '?'
    toy2_msg = "I think it's time for the " + cat.toy2 + "!!!"
    snack_msg = "I'm hungry!! I want " + cat.snack + "!"
    activity1_msg = "Whachu up to? I'm busy " + cat.activity1 + "..."
    activity2_msg = "Me? I'm just " + cat.activity2 + "..."
    msg1 = "I'm scared of the blender and the vacuum!"
    msg2 = "I like being in small boxes."
    msg3 = "Sometimes I like to tear through the apartment, meowing loudly."
    msg4 = "It is a cat's duty to appear aloof at all times."
    msg5 = "Got any catnip?"
    msg6 = "I'M HUNGRY"
    msg7 = "zzzzzZZZZZZZ"
    msg8 = "mrrrowwwww"
    msg9 = ".........."

    cat_responses = [toy1_msg, toy2_msg, snack_msg, activity1_msg, activity2_msg,
                     msg1, msg2, msg3, msg4, msg5, msg6, msg7, msg8, msg9]


    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    # Start our TwiML response
    resp = MessagingResponse()

    if (body == 'hey') or (body == 'Hey') or (body == 'Hi') or (body == 'hi'):
        resp.message("Hi! Where's my " + cat.snack + "?!")
    elif (body == 'bye') or (body == 'Bye'):
        resp.message("Bye? I'm just going to text you again later.")
    elif (body == "sup?") or (body == "Sup?"):
        resp.message("Sup? What year do you think it is right meow?")
    elif (body == "I'm bored") or (body == "i'm bored"):
        resp.message("You can borrow my " + toy1 + "for a bit if you want.")
    else:
        reply = random.choice(cat_responses)
        resp.message(reply)

    return str(resp)


if __name__ == "__main__":

    app.debug = False
    #app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app, location="postgres:///cattexts")
    print "Connected to DB."

    app.run(port=5000, host='0.0.0.0')

    atexit.register(lambda: scheduler.shutdown())
