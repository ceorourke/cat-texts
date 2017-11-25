from flask import Flask, request, redirect, render_template
# from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import schedule
import time
from model import connect_to_db, db, User, Cat

from datetime import datetime
from pytz import timezone

# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
phone_number = os.environ.get("phone_number")

app = Flask(__name__)

def daily_text():

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, " + name + " here. I'm pretty sure it's time to feed me!!")

    print(message.sid)


if __name__ == "__main__":
    connect_to_db(app)

    user_id = User.query.filter_by(phone_number=phone_number).first()
    user_id = user_id.user_id
    dinner_time = db.session.query(Cat.dinner_time).filter(User.user_id==user_id).first()
    dinner_time = str(dinner_time[0])
    # TODO need to convert dinner_time to UTC
    # dinner_time = "00:17"
    print dinner_time
    name = db.session.query(Cat.name).filter(User.user_id==user_id).first()
    name = str(name[0])
    print name
    schedule.every().day.at(dinner_time).do(daily_text)
    # schedule.every(5).seconds.do(daily_text)

    while True:
        schedule.run_pending()
        time.sleep(1)


    # Current time in UTC
    now_utc = datetime.now(timezone('UTC'))
    # Convert to US/Pacific time zone
    now_pacific = now_utc.astimezone(timezone('US/Pacific'))

