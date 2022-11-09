from dotenv import load_dotenv

load_dotenv()

import os
import sys

this = sys.modules[__name__]

MAIL_PASSWORD: None | str = ''
STRIPE_API_KEY: None | str = ''
IS_REAL_EMAIL_BEARER: None | str = ''
TWILIO_ACCOUNT_SID: None | str = ''
TWILIO_AUTH_TOKEN: None | str = ''
DB_PATH: None | str = None
SECRET_KEY: None | str = ''

for (k, v) in list(this.__dict__.items()):
	key = str(k)
	if not key.startswith('__') and key.isupper():
		setattr(this, k, os.environ.get(k))
