# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

from dotenv import load_dotenv
load_dotenv()


# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = "ACcae4454ffa2c5db7f5f368cec0ef4af0"
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

call = client.calls.create(
  url="https://wise-agent.onrender.com/voice",
  to="+919777256250",
  from_="+19895192066"
)

print(call.sid)

