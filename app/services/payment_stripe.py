import stripe
from autologging import traced

from core.services.payment_service import PaymentService


@traced
class PaymentStripe(PaymentService):
	def __init__(self, api_key: str):
		stripe.api_key = api_key
		self.preferred_locales = ['si']

	def create_customer(self, entity_id: str, full_name, email: str, phone: str):
		return stripe.Customer.create(
			email=email,
			name=full_name,
			phone=phone,
			metadata={
				'entity_id': entity_id
			})

	def delete_customer(self, email):
		return stripe.Customer.delete()

	def list_customers(self, email: str):
		return stripe.Customer.list(email=email)

	def search_customer(self, query: str):
		return stripe.Customer.search(query=query)
