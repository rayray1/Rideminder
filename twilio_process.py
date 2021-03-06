# Twilio processes and set up
import twilio
from twilio.rest import TwilioRestClient
import os

# Twilio Account Information
TWILIO_ACCOUNT_SID=os.environ.get("TWILIO_ACCOUNT_SID", ['TWILIO_ACCOUNT_SID'])
TWILIO_AUTH_TOKEN=os.environ.get("TWILIO_AUTH_TOKEN", ['TWILIO_AUTH_TOKEN'])
TWILIO_NUMBER=str(os.environ.get("TWILIO_NUMBER", ['TWILIO_NUMBER']))


def send_text_message(phone):
    """sends the text message to the user once the destination is within WALK_RADIUS"""

    print 'sending text message'

    try:
        # twilio.rest.TwilioRestClient
        client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body="You are within 1 minute of your destination, thank you for using Rideminder",
            to=phone,
            from_=TWILIO_NUMBER
        )
    except twilio.TwilioRestException as e:
        print e
