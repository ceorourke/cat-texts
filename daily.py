from flask import Flask, request, redirect, render_template
# from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import threading
import schedule
import time
from model import connect_to_db, db, User, Cat

# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
# phone_number = os.environ.get("phone_number") # my phone number
app = Flask(__name__)
################################################################################

def daily_text():

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, " + name + " here. I'm pretty sure it's time to feed me!!")

    print(message.sid)


if __name__ == "__main__":
    connect_to_db(app)

    for user in User.query.all():
        user_id = user.user_id
        for cat in Cat.query.filter_by(user_id=user_id).all():
            dinner_time = db.session.query(Cat.dinner_time).filter(User.user_id==user_id).first()
            # if multiple cats (not currently supported) i think .first
            # may not be the way to go, but .one() is throwing an error which is weird
            minutes = dinner_time[0].minute
            hour = dinner_time[0].hour

            if len(str(hour)) < 2:
                new_hour = "0"
                new_hour += str(hour)
            else:
                new_hour = str(hour)

            if len(str(minutes)) < 2:
                new_minutes = "0"
                new_minutes += str(minutes) 
            else:
                new_minutes = str(minutes)

            this_time = new_hour + ":" + new_minutes
            name = db.session.query(Cat.name).filter(User.user_id==user_id).first()
            name = str(name[0])
            phone_number = user.phone_number

            print cat.name
            print cat.dinner_time
            print user.phone_number

            # need to find way to run these asynchronously, currently it does the 
            # first one and stays there forever. how can I run the others?
            # use threading? need to read more about this

            schedule.every().day.at(this_time).do(daily_text)
            # can't pass variables to daily_text it seems
            # this doesn't work if i pass phone_number, for example

            while True:
                schedule.run_pending()
                time.sleep(1)









