from flask import Flask, request, redirect, render_template
from twilio.twiml.messaging_response import MessagingResponse
import random
from twilio.rest import Client
import os
# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
phone_number = os.environ.get("phone_number")

app = Flask(__name__)
############################################################################

CAT_INFO = {}

@app.route("/")
def main():
    """Render main page"""

    return render_template("homepage.html")

@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    toy1 = 'Can we play with my ' + CAT_INFO['cat_toy'] + '?'
    toy2 = "I think it's time for the " + CAT_INFO['cat_toy2'] + "!!!"
    snack = "I'm hungry!! I want " + CAT_INFO['cat_snack'] + "!"
    activity1 = "Whachu up to? I'm busy " + CAT_INFO['cat_activity'] + "..."
    activity2 = "Me? I'm just " + CAT_INFO['cat_activity2'] + "..."

    cat_responses = [toy1, toy2, snack, activity1, activity2]
    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'hey' or body == 'Hey':
        resp.message("Hi! Where's my " + CAT_INFO['cat_snack'] + "?!")
    elif body == 'bye' or body == 'Bye':
        resp.message("Bye? I'm just going to text you again later.")
    else:
        reply = random.choice(cat_responses)
        resp.message(reply)

    return str(resp)


@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    """Welcome to the user to Cat Texts"""

    CAT_INFO['cat_name'] = request.args.get('cat-name')
    CAT_INFO['cat_snack'] = request.args.get('cat-snack')
    CAT_INFO['cat_activity'] = request.args.get('cat-activity')
    CAT_INFO['cat_activity2'] = request.args.get('cat-activity2')
    CAT_INFO['cat_toy'] = request.args.get('cat-toy')
    CAT_INFO['cat_toy2'] = request.args.get('cat-toy2')


    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, it's " + CAT_INFO['cat_name'] + ". I like " + CAT_INFO['cat_snack'] + "!")

    print(message.sid)
    return render_template("homepage.html")

if __name__ == "__main__":

    app.run(port=5000, host='0.0.0.0')




