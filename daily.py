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

    # TODO currently this is pulling my phone number from secrets.sh
    # should change to query db for all phone numbers and do this for everyone
    # ...even though technically everything in the db is my phone number
    # since I have the trial Twilio account. could shoot off texts at different
    # times for testing purposes so I'm not waiting a full 24 hours 

    user_id = User.query.filter_by(phone_number=phone_number).first()
    user_id = user_id.user_id
    dinner_time = db.session.query(Cat.dinner_time).filter(User.user_id==user_id).first()

    minutes = dinner_time[0].minute
    hour = dinner_time[0].hour

    # this seems to be 7 minutes EARLY, so adding 7 minutes to make it correct

    if (minutes + 7) >= 60: # check if adding 7 minutes pushes it over to next hour
        if hour == 23: # check if the hour is 11 pm / 23:XX
            hour = 0 # make it 00:XX
        else:
            hour += 1
        if (minutes + 7) == 60: # convert minutes
            minutes = 0
        else:
            minutes = (minutes + 7) - 60  # wrap around ... 
    else:          
        minutes += 7

    this_timezone = timezone('US/Pacific') # needs a timezone to convert to UTC
    date = dinner_time[0].replace(minute=minutes, tzinfo=this_timezone) 
    utc = pytz.utc
    date = date.astimezone(utc) # convert to UTC

    this_time = str(date.hour) + ":" + str(date.minute)
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







