import uvicorn

from api import api
from app import env
from app.db import seed

env.init()
EMAIL.init_api()
STRIPE.init_api()
TWILIO.init_api()
seed.init()
api.init()

if __name__ == "__main__":
	uvicorn.run(api.app, host="0.0.0.0", port=8000)
