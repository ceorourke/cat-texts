from flask import Flask, request, redirect, render_template
# from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import threading
import schedule
import time
from model import connect_to_db, db, User, Cat
from helper_functions import make_minutes, make_hour

# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)

app = Flask(__name__)
################################################################################

def daily_text():

    message = client.messages.create(
    to=phone_number,
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, " + name + " here. I'm pretty sure it's time to feed me!!")

    print(message.sid)

def job():
    print("I'm running on thread %s" % threading.current_thread())
    print name

#def run_threaded(job_func):
#    job_thread = threading.Thread(target=job_func)
#    job_thread.start()

if __name__ == "__main__":
    connect_to_db(app)
    thread_hash = {}

    for cat in Cat.query.all():
        dinner_time = cat.dinner_time

        minutes = make_minutes(dinner_time.minute)
        hour = make_hour(dinner_time.hour)

        this_time = hour + ":" + minutes

        name = cat.name
        phone_number = cat.user.phone_number

        print this_time
        print name
        print phone_number

        # schedule.every().day.at(this_time).do(daily_text)

        # schedule.every().day.at(this_time).do(run_threaded, daily_text)
        thread_hash[cat] = threading.Thread(target=job)
        job_thread.start()

        while 1:
            schedule.run_pending()
            time.sleep(1)

    for cat in Cat.query.all():
        thread_hash[cat].join()
