from flask import Flask, request, redirect, render_template, session, flash
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Cat
from helper_functions import *
from pytz import timezone
import pytz
import random
import bcrypt
import os
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
################################################################################

@app.route("/")
def main():
    """Render main page"""

    return render_template("home.html")


@app.route("/login", methods=["POST"])
def login():
    """Attempt to log the user in"""

    email = request.form.get("email")
    password = request.form.get("password")

    existing_email = User.query.filter_by(email=email).first()

    if existing_email is not None and existing_email.password == password:
        # add user to session
        session["user_id"] = existing_email.user_id
        user_id = session["user_id"]

        flash("Successfully logged in!")

        cat = Cat.query.filter_by(user_id=user_id).first()

        return render_template("main.html", name=cat.name, toy1=cat.toy1, 
                                            toy2=cat.toy2, snack=cat.snack, 
                                            activity1=cat.activity1,
                                            activity2=cat.activity2, 
                                            dinner_time=cat.dinner_time)

    elif existing_email is None:
        flash("Incorrect email.")
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

    return render_template("register.html")

@app.route("/register", methods=["GET", "POST"])
def register_process():
    """Get information from registration form."""

    email = request.form.get("email")

    password = request.form.get("password")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    phone = request.form.get("phone")
    country_code = '+1'
    phone = ''.join(num for num in phone if num not in '-')
    phone = country_code + phone

    name = request.form.get('cat-name')
    dinner_time = request.form.get('dinner-time')
    ampm = request.form.get('ampm')

    time = parse_time(dinner_time)
    hour = time[0]
    minutes = time[1]
    hour = make_24_hour_time(ampm, hour)
    date = convert_to_utc(hour, minutes)

    snack = request.form.get('cat-snack')
    activity1 = request.form.get('cat-activity')
    activity2 = request.form.get('cat-activity2')
    toy1 = request.form.get('cat-toy')
    toy2 = request.form.get('cat-toy2')

    existing_email = User.query.filter_by(email=email).first()

    # check if the email is in use
    if existing_email is None:
        new_user = User(email=email, password=hashed, phone_number=phone)
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

        message = client.messages.create(
        to=phone, 
        from_="+14138486585",
        # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
        body="Hi, it's " + name + ". I like " + snack + "! Feed me at " + dinner_time + "!")

        print(message.sid)

        flash("Successfully registered " + email + "!")
        return render_template("thanks.html")

    else:
        flash("Email already in use")
        # TODO probably handle this in AJAX on the form

    return redirect("/")


@app.route("/main")
def main_page():
    """Render main page"""

    user_id = session["user_id"]

    cat = Cat.query.filter_by(user_id=user_id).first()

    print "*********"
    print "in main"
    print cat.dinner_time
    print cat.dinner_time.tzinfo

    return render_template("main.html", name=cat.name, toy1=cat.toy1, 
                                        toy2=cat.toy2, snack=cat.snack, 
                                        activity1=cat.activity1,
                                        activity2=cat.activity2, 
                                        dinner_time=cat.dinner_time)


@app.route("/update")
def show_update():
    """Show update page"""

    return render_template("update.html")


@app.route("/update", methods=['POST'])
def do_update():
    """Update details in db"""

    name = request.form.get('cat-name')
    dinner_time = request.form.get('dinner-time')
    ampm = request.form.get('ampm')
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
        hour = time[0]
        minutes = time[1]
        hour = make_24_hour_time(ampm, hour)
        date = convert_to_utc(hour, minutes)    

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

    flash("Successfully updated " + cat.name + "'s info!")

    return render_template("main.html", name=cat.name, toy1=cat.toy1, 
                                        toy2=cat.toy2, snack=cat.snack, 
                                        activity1=cat.activity1,
                                        activity2=cat.activity2, 
                                        dinner_time=cat.dinner_time)


@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""

    phone = request.values.get('From', None)
    user_id = User.query.filter_by(phone_number=phone).first()
    user_id = user_id.user_id

    name = db.session.query(Cat.name).filter(User.user_id==user_id).first()
    toy1 = db.session.query(Cat.toy1).filter(User.user_id==user_id).first()
    toy2 = db.session.query(Cat.toy2).filter(User.user_id==user_id).first()
    snack = db.session.query(Cat.snack).filter(User.user_id==user_id).first()
    activity1 = db.session.query(Cat.activity1).filter(User.user_id==user_id).first()
    activity2 = db.session.query(Cat.activity2).filter(User.user_id==user_id).first()

    name = str(name[0])
    toy1 = str(toy1[0])
    toy2 = str(toy2[0])
    snack = str(snack[0])
    activity1 = str(activity1[0])
    activity2 = str(activity2[0])

    toy1_msg = 'Can we play with my ' + toy1 + '?'
    toy2_msg = "I think it's time for the " + toy2 + "!!!"
    snack_msg = "I'm hungry!! I want " + snack + "!"
    activity1_msg = "Whachu up to? I'm busy " + activity1 + "..."
    activity2_msg = "Me? I'm just " + activity2 + "..."

    cat_responses = [toy1_msg, toy2_msg, snack_msg, activity1_msg, activity2_msg]

    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'hey' or body == 'Hey':
        resp.message("Hi! Where's my " + snack + "?!")

    elif body == 'bye' or body == 'Bye':
        resp.message("Bye? I'm just going to text you again later.")
    else:
        reply = random.choice(cat_responses)
        resp.message(reply)

    return str(resp)


if __name__ == "__main__":

    from flask import Flask

    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)
    print "Connected to DB."

    app.run(port=5000, host='0.0.0.0')


