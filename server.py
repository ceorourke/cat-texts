from flask import Flask, request, redirect, render_template, session, flash
from twilio.twiml.messaging_response import MessagingResponse
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Cat
import random
from twilio.rest import Client
import os
import schedule
import time
from datetime import datetime
from pytz import timezone
import pytz
# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
phone_number = os.environ.get("phone_number")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
############################################################################

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

        flash("Successfully logged in!")

        user_id = session["user_id"]

        name = db.session.query(Cat.name).filter(User.user_id==user_id).first()
        toy1 = db.session.query(Cat.toy1).filter(User.user_id==user_id).first()
        toy2 = db.session.query(Cat.toy2).filter(User.user_id==user_id).first()
        snack = db.session.query(Cat.snack).filter(User.user_id==user_id).first()
        activity1 = db.session.query(Cat.activity1).filter(User.user_id==user_id).first()
        activity2 = db.session.query(Cat.activity2).filter(User.user_id==user_id).first()
        dinner_time = db.session.query(Cat.dinner_time).filter(User.user_id==user_id).first()

        name = str(name[0])
        toy1 = str(toy1[0])
        toy2 = str(toy2[0])
        snack = str(snack[0])
        activity1 = str(activity1[0])
        activity2 = str(activity2[0])
        dinner_time = str(dinner_time[0])

        return render_template("main.html", name=name, toy1=toy1, toy2=toy2,
                                            snack=snack, activity1=activity1,
                                            activity2=activity2, dinner_time=dinner_time)

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
    phone = request.form.get("phone")
    country_code = '+1'
    phone = ''.join(num for num in phone if num not in '-')
    phone = country_code + phone

    name = request.form.get('cat-name')
    dinner_time = request.form.get('dinner-time')

    #TODO factor this out

    date = datetime.now()
    this_timezone = timezone('US/Pacific')
    # currently just testing this, only works for 24 hour format time
    # and only for 2 digit hours i.e. 19:00
    # (needs to be input like above, will make more flexible later)
    hour = int(dinner_time[0:2])
    minutes = int(dinner_time[3:])
    # date = date.replace(hour=hour, minute=minutes, second=0, tzinfo=this_timezone)
    date = date.replace(hour=hour, minute=minutes, second=0, tzinfo=None)
    # convert to UTC
    utc = pytz.utc
    # date = date.astimezone(utc)

    snack = request.form.get('cat-snack')
    activity1 = request.form.get('cat-activity')
    activity2 = request.form.get('cat-activity2')
    toy1 = request.form.get('cat-toy')
    toy2 = request.form.get('cat-toy2')
    current_user = session["user_id"]

    existing_email = User.query.filter_by(email=email).first()

    # check if the email is in use
    if existing_email is None:
        new_user = User(email=email, password=password, phone_number=phone)
        # TODO hash password
        db.session.add(new_user)
        db.session.commit()

        new_cat = Cat(user_id=current_user, name=name, dinner_time=date, 
                  snack=snack, activity1=activity1, activity2=activity2, 
                  toy1=toy1, toy2=toy2)
        db.session.add(new_cat)
        db.session.commit()

        message = client.messages.create(
        to=phone_number, 
        from_="+14138486585",
        # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
        body="Hi, it's " + name + ". I like " + snack + "! Feed me at " + dinner_time + "!")

        print(message.sid)

        flash("Successfully registered " + email + "!")
        return render_template("thanks.html")

    else:
        flash("Email already in use")
        # TODO probably handle this in AJAX on the form and be more specific
        # as to whether it was the username or email that failed


    return redirect("/")

@app.route("/update")
def show_update():
    """Show update page"""

    return render_template("update.html")

@app.route("/update", methods=['POST'])
def do_update():
    """Update details in db"""

    #TODO this isn't actually updating in DB :(

    current_user = session["user_id"]
    cat = db.session.query(Cat).filter(User.user_id==current_user).first()

    name = request.form.get('cat-name')
    dinner_time = request.form.get('dinner-time')
    # TODO convert to UTC?
    snack = request.form.get('cat-snack')
    activity1 = request.form.get('cat-activity')
    activity2 = request.form.get('cat-activity2')
    toy1 = request.form.get('cat-toy')
    toy2 = request.form.get('cat-toy2')

    if name:
        cat.name = name
    else: 
        name = db.session.query(Cat.name).filter(User.user_id==current_user).first()
        name = str(name[0])
    if dinner_time:
        cat.dinner_time = dinner_time
    else:
        dinner_time = db.session.query(Cat.dinner_time).filter(User.user_id==current_user).first()
        dinner_time = str(dinner_time[0])
    if toy1:
        cat.toy1 = toy1
    else:
        toy1 = db.session.query(Cat.toy1).filter(User.user_id==current_user).first()
        toy1 = str(toy1[0])
    if toy2:
        cat.toy2 = toy2
    else:
        toy2 = db.session.query(Cat.toy2).filter(User.user_id==current_user).first()
        toy2 = str(toy2[0])
    if snack:
        cat.snack = snack
    else:
        snack = db.session.query(Cat.snack).filter(User.user_id==current_user).first()
        snack = str(snack[0])
    if activity1:
        cat.activity1 = activity1
    else:
        activity1 = db.session.query(Cat.activity1).filter(User.user_id==current_user).first()
        activity1 = str(activity1[0])
    if activity2:
        cat.activity2 = activity2
    else:
        activity2 = db.session.query(Cat.activity2).filter(User.user_id==current_user).first()
        activity2 = str(activity2[0])

    db.session.commit
    flash("Successfully updated " + cat.name + "'s info!")

    return render_template("main.html", name=name, toy1=toy1, toy2=toy2,
                                        snack=snack, activity1=activity1,
                                        activity2=activity2, dinner_time=dinner_time)


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


