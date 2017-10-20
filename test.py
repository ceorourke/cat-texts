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

@app.route("/")
def main():
    """Render main page"""

    return render_template("homepage.html")

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    cat_facts = ["Cats use their tails for balance and have nearly 30 individual bones in them! \
                 <To cancel Daily Cat Facts, reply 'oh god'>",
                 "In ancient Egypt killing a cat was a crime punishable by death. Thanks for choosing Cat Facts!",
                 "Did you know there are about 100 distinct breeds of domestic cat? Plenty of furry love!",
                 "Welcome to Cat Facts! Did you know that the first cat show was held in 1871 at the Crystal Palace in London? Mee-wow!",
                 "Cats bury their feces to cover their trails from predators."]

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'hello':
        resp.message("Meeeow! Welcome to Cat Facts!")
    elif body == 'bye':
        resp.message("Goodnight meow!")
    else:
        reply = random.choice(cat_facts)
        resp.message(reply)

    return str(resp)

def welcome():
    """Welcome to the user to Cat Facts"""

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Thanks for signing up for Cat Facts! You will now receive daily fun facts about CATS! >o< \
          Reply 'hello' to say hi, 'bye' to say goodnight, and anything else to get a CAT FACT!")

    print(message.sid)

if __name__ == "__main__":
    welcome()
    app.run(port=5000, host='0.0.0.0')




