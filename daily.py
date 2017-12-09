from flask import Flask, request, redirect, render_template
from twilio.rest import Client
import os
import time 
import schedule
from functools import partial
from model import connect_to_db, db, User, Cat
from helper_functions import make_minutes, make_hour

# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)

app = Flask(__name__)
################################################################################

def daily_text(name, phone_number):

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, " + name + " here. I'm pretty sure it's time to feed me!!")

    print(message.sid)

def job(name):
    """Test functionality""" 

    print "RUNNING JOB -----------------"
    print name
    print "-----------------------------"

def schedule_texts():
    """Schedule texts every day for each cat"""

    for cat in Cat.query.all():
        dinner_time = cat.dinner_time

        minutes = make_minutes(dinner_time.minute)
        hour = make_hour(dinner_time.hour)

        this_time = hour + ":" + minutes

        name = cat.name
        phone_number = cat.user.phone_number

        bound_f = partial(daily_text, name, phone_number)
      
        print "SCHEDULING JOB -----------"
        print name
        print "---------------------------"

        schedule.every().day.at(this_time).do(bound_f)

    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    connect_to_db(app)

    



