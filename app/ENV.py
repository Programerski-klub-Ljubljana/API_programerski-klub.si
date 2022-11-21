import os

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.environ.get('DB_PATH', None)
SECRET_KEY = os.environ['SECRET_KEY']

MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
MAIL_PORT = int(os.environ['MAIL_PORT'])

TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_FROM_NUMBER = os.environ['TWILIO_FROM_NUMBER']

STRIPE_API_KEY = os.environ['STRIPE_API_KEY']
MAIL_SUPPRESS_SEND = bool(int(os.environ['MAIL_SUPPRESS_SEND']))
