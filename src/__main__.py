import uvicorn

from src import env, api
from src.db import seed
from src.services import EMAIL, TWILIO, STRIPE

env.init()
EMAIL.init()
STRIPE.init()
TWILIO.init()
seed.init()
api.init()

if __name__ == "__main__":
	uvicorn.run(api.app, host="0.0.0.0", port=8000)
