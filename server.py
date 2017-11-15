from flask import Flask, request, redirect, render_template, session, flash
from twilio.twiml.messaging_response import MessagingResponse
from jinja2 import StrictUndefined
import random
from twilio.rest import Client
import os
import schedule
import time
from datetime import datetime
from pytz import timezone
from model import connect_to_db, db, User, Cat
# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
phone_number = os.environ.get("phone_number")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
############################################################################

# CAT_INFO = {}

# CAT_INFO['dinner_time'] = "8:57"

@app.route("/")
def main():
    """Render main page"""

    return render_template("home.html")

@app.route("/login", methods=["GET"])
def attempt_login():
    """Show login page"""

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
        return render_template("homepage.html")

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

    # TODO put this somewhere on the page!
    return redirect("/")

@app.route("/register", methods=["GET"])
def register():
    """Show registration form"""

    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_process():
    """Get information from registration form."""

    email = request.form.get("email")
    password = request.form.get("password")

    existing_email = User.query.filter_by(email=email).first()

    # check if the username is in use
    if existing_email is None:
        #check if the email is in use
        new_user = User(email=email, password=password)

        # TODO hash password

        db.session.add(new_user)
        db.session.commit()

        flash("Successfully registered " + email + "!")
        return redirect("/")

    else:
        flash("Username or email already in use")
        # TODO probably handle this in AJAX on the form and be more specific
        # as to whether it was the username or email that failed

    return redirect("/")


@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""

    # user_id = session["user_id"]
    user_id = 1
    name = str(db.session.query(Cat.name).filter(User.user_id==user_id).first())
    toy1 = str(db.session.query(Cat.toy1).filter(User.user_id==user_id).first())
    toy2 = str(db.session.query(Cat.toy2).filter(User.user_id==user_id).first())
    snack = db.session.query(Cat.snack).filter(User.user_id==user_id).first()
    activity1 = str(db.session.query(Cat.activity1).filter(User.user_id==user_id).first())
    activity2 = str(db.session.query(Cat.activity2).filter(User.user_id==user_id).first())

    print type(snack)
    snack = str(snack)
    print type(snack)
    snack = snack.encode('utf-8')
    # TODO trying to get this to not be in unicode!!

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
        # resp.message("Hi! Where's my " + CAT_INFO['cat_snack'] + "?!")
        resp.message("Hi! Where's my " + snack + "?!")

    elif body == 'bye' or body == 'Bye':
        resp.message("Bye? I'm just going to text you again later.")
    else:
        reply = random.choice(cat_responses)
        resp.message(reply)

    return str(resp)


@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    """Welcome to the user to Cat Texts"""

    # TODO maybe move this all to registration? probably better UX

    name = request.args.get('cat-name')
    dinner_time = request.args.get('dinner-time')
    snack = request.args.get('cat-snack')
    activity1 = request.args.get('cat-activity')
    activity2 = request.args.get('cat-activity2')
    toy1 = request.args.get('cat-toy')
    toy2 = request.args.get('cat-toy2')
    current_user = session["user_id"]

    new_cat = Cat(name=name, user_id=current_user, dinner_time=dinner_time, 
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

    return render_template("thanks.html")


def daily_text():

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, " + CAT_INFO['cat_name'] + " here. I'm pretty sure it's dinner time!")
    # body = "hi I'm working")

    print(message.sid)


if __name__ == "__main__":

    from flask import Flask

    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)
    print "Connected to DB."

    app.run(port=5000, host='0.0.0.0')

    # runs every day at dinner time
    # schedule.every().day.at(str(CAT_INFO['dinner_time'])).do(daily_text)
    # # just testing functionality, comment out above line
    # # schedule.every(5).seconds.do(daily_text) 

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # having trouble here - I can only get the scheduled job to work if I put 
    # app.run at the end, however the CAT_INFO dictionary has no info in it yet
    # obviously, because the user hasn't entered it yet. 

    # Current time in UTC
    now_utc = datetime.now(timezone('UTC'))
    # Convert to US/Pacific time zone
    now_pacific = now_utc.astimezone(timezone('US/Pacific'))

