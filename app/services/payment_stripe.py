import time
from datetime import datetime

import stripe
from autologging import traced

from core import cutils
from core.services.payment_service import PaymentService, PaymentCustomer


@traced
class StripeResParser:
	@classmethod
	def parse_customer(cls, stripe_customer: stripe.Customer) -> PaymentCustomer:
		if stripe_customer.last_response is not None:
			stripe_customer = stripe_customer.last_response.data
			entity_id = stripe_customer['metadata']['entity_id']
			created = stripe_customer['created']
		else:
			entity_id = stripe_customer.metadata.entity_id
			created = stripe_customer.created

		return cutils.call(PaymentCustomer, **{
			**stripe_customer,
			'entity_id': entity_id,
			'created': datetime.utcfromtimestamp(created)
		})


@traced
class PaymentStripe(PaymentService, StripeResParser):

	def __init__(self, api_key: str):
		stripe.api_key = api_key
		self.page_limit = 100
		self.tries_before_fail = 30
		self.sleep_before_next_trie = 2

	def create_customer(self, customer: PaymentCustomer) -> PaymentCustomer:
		"""If customer allready exists do not create it but joust return..."""
		old_customer = self.get_customer(customer.entity_id, with_tries=False)

		if old_customer is not None:
			return old_customer

		return self.parse_customer(stripe.Customer.create(
			name=customer.name, description=customer.description,
			phone=customer.phone, email=customer.email,
			metadata={'entity_id': customer.entity_id}))

	def list_customers(self) -> list[PaymentCustomer]:
		all_customers = []

		starting_after = None
		while True:
			customers: stripe.Customer = stripe.Customer.list(limit=self.page_limit, starting_after=starting_after)
			all_customers += customers.data
			if customers.has_more:
				starting_after = customers[-1].id
			else:
				break

		return [self.parse_customer(c) for c in all_customers]

	def get_customer(self, entity_id: str, with_tries: bool = True) -> PaymentCustomer | None:
		tries = self.tries_before_fail if with_tries else 1

		while True:
			customers = self.search_customer(f"metadata['entity_id']:'{entity_id}'")
			tries -= 1

			if len(customers) == 0 and tries <= 0:
				return None
			elif len(customers) == 1:
				return customers[0]
			elif len(customers) > 1:
				raise Exception(f"Customers with duplicated entity_id: {customers}")

			time.sleep(self.sleep_before_next_trie)

	def search_customer(self, query: str) -> list[PaymentCustomer]:
		return [self.parse_customer(c) for c in stripe.Customer.search(query=query, limit=self.page_limit).data]

	def delete_customer(self, entity_id: str, with_tries: bool = True) -> bool:
		customer = self.get_customer(entity_id=entity_id, with_tries=with_tries)

		if customer is None:
			return False

		tries = self.tries_before_fail

		while True:

			try:
				return stripe.Customer.delete(sid=customer.id).deleted
			except Exception as err:
				pass

			tries -= 1
			if tries == 0:
				return False
			time.sleep(1)
