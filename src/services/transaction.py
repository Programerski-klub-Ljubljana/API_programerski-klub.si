import os

import stripe

stripe.api_key = os.environ['STRIPE_API_KEY']
