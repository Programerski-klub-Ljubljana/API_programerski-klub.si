import os
import sys

from dotenv import load_dotenv

load_dotenv()
this = sys.modules[__name__]

MAIL_PASSWORD: None | str = ''
STRIPE_API_KEY: None | str = ''
IS_REAL_EMAIL_BEARER: None | str = ''
TWILIO_ACCOUNT_SID: None | str = ''
TWILIO_AUTH_TOKEN: None | str = ''
DB_PATH: None | str = None

for (k, v) in list(this.__dict__.items()):
	if not str(k).startswith('__'):
		setattr(this, k, os.environ.get(k, default=v))
