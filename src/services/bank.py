import os

import stripe

def init():
	stripe.api_key = os.environ['STRIPE_API_KEY']
	print(stripe.Customer.create(description="asdfsdfdf"))
