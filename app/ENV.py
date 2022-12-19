import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ['SECRET_KEY']

DB_PATH = os.environ.get('DB_PATH', None)
DB_DEFAULT_PASSWORD = os.environ.get("DB_DEFAULT_PASSWORD", 'geslo')

MAIL_PORT = int(os.environ['MAIL_PORT'])
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
MAIL_SUPPRESS_SEND = bool(int(os.environ['MAIL_SUPPRESS_SEND']))

TWILIO_SERVICE_SID = os.environ['TWILIO_SERVICE_SID']
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_FROM_NUMBER = os.environ['TWILIO_FROM_NUMBER']

STRIPE_API_KEY = os.environ['STRIPE_API_KEY']

GITHUB_PRIVATE_KEY_PATH = os.environ['GITHUB_PRIVATE_KEY_PATH']
GITHUB_APP_ID = os.environ['GITHUB_APP_ID']

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'TRACE')
