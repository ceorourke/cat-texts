from flask import Flask, request, redirect, render_template
# from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import schedule
import time
from model import connect_to_db, db, User, Cat

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

    # currently just testing this, only works for 24 hour format time
    # and only for 2 digit hours i.e. 19:00
    # (needs to be input like above, will make more flexible later)
    # hour = dinner_time[0:2]
    # hour = int(hour)
    # minutes = int(dinner_time[3:])
    minutes = dinner_time[0].minute + 7
    # this seems to be 7 minutes EARLY, so adding 7 minutes to make it correct
    # note this is not flexible if it's 14:59 for example, just a hacky workaround for now
    # put in 30
    # got back 23

    this_timezone = timezone('US/Pacific')
    date = dinner_time[0].replace(minute=minutes, tzinfo=this_timezone) # needs a timezone to convert to UTC
    # convert to UTC
    utc = pytz.utc
    date = date.astimezone(utc)

    hour = date.hour
    minute = date.minute

    this_time = str(hour) + ":" + str(minute)
    print this_time
    name = db.session.query(Cat.name).filter(User.user_id==user_id).first()
    name = str(name[0])
    print name
    schedule.every().day.at(this_time).do(daily_text)
    # schedule.every().day.at("21:10").do(daily_text)
    # schedule.every(5).seconds.do(daily_text)

    while True:
        schedule.run_pending()
        time.sleep(1)







