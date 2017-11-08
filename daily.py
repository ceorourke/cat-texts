from flask import Flask, request, redirect, render_template
# from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import schedule
import time
from server import CAT_INFO
# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
phone_number = os.environ.get("phone_number")

app = Flask(__name__)

print CAT_INFO

# @app.route("/sms", methods=['POST'])
def daily_text():

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, " + CAT_INFO['cat_name'] + "here. I'm pretty sure it's dinner time!")
    # body = "hi I'm working")

    print(message.sid)

# schedule.every().day.at(CAT_INFO['dinner_time']).do(daily_text)
schedule.every(5).seconds.do(daily_text)

while True:
    schedule.run_pending()
    time.sleep(1)

