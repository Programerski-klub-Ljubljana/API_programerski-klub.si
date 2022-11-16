import os
import sys

from dotenv import load_dotenv

this = sys.modules[__name__]

MAIL_PASSWORD: None | str = ''
STRIPE_API_KEY: None | str = ''
IS_REAL_EMAIL_BEARER: None | str = ''
TWILIO_ACCOUNT_SID: None | str = ''
TWILIO_AUTH_TOKEN: None | str = ''
DB_PATH: None | str = None
SECRET_KEY: None | str = ''
PHONE_CODE: str = '+386'
TOKEN_URL: str = '/user/login'
TOKEN_EXPIRE: int = 20


def init():
	load_dotenv()
	for (k, v) in list(this.__dict__.items()):
		key = str(k)
		if not key.startswith('__') and key.isupper():
			val = os.environ[k]
			if val.isnumeric():
				val = float(val)
			elif len(val) == 0:
				val = None
			setattr(this, k, val)
