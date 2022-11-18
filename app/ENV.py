import os
import sys

from dotenv import load_dotenv

this = sys.modules[__name__]
inited: bool = False

DB_PATH: None | str = None
SECRET_KEY: None | str = ''

MAIL_USERNAME: None | str = ''
MAIL_PASSWORD: None | str = ''
MAIL_PORT: None | int = 0

TWILIO_ACCOUNT_SID: None | str = ''
TWILIO_AUTH_TOKEN: None | str = ''

STRIPE_API_KEY: None | str = ''


def init():
	this.inited = True
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
