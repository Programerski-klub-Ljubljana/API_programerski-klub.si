import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import stripe
from autologging import traced

from core import cutils
from core.services.payment_service import PaymentService, Customer, Subscription


@dataclass
class StripeObj(ABC):

	@staticmethod
	@abstractmethod
	def parse(self, kwargs):
		pass

	@staticmethod
	@abstractmethod
	def create(obj):
		pass


class StripeCustomer(Customer, StripeObj):

	def json(self):
		_dict = self.__dict__.copy()
		_dict['metadata'] = {'entity_id': self.entity_id}
		_dict['created'] = self.created.timestamp()
		return _dict

	@staticmethod
	def parse(**kwargs) -> Customer:
		return cutils.call(StripeCustomer, **{
			**kwargs,
			'entity_id': kwargs['metadata']['entity_id'],
			'created': datetime.fromtimestamp(kwargs['created'])})

	@staticmethod
	def create(obj: Customer):
		kwargs = dict(stripe.Customer.create(
			name=obj.name, description=obj.description,
			phone=obj.phone, email=obj.email,
			metadata={'entity_id': obj.entity_id}))

		return cutils.call(StripeCustomer, **{
			**kwargs,
			'created': datetime.fromtimestamp(kwargs.pop('created')),
			'entity_id': kwargs['metadata']['entity_id']
		})


class StripeSubscription(Subscription, StripeObj):

	@staticmethod
	def create(obj: Subscription):
		kwargs = dict(stripe.Subscription.create(
			description=obj.description,
			items=[{'price': price_id} for price_id in obj.prices],
			customer=obj.customer.id,
			collection_method=obj.collection_method.value,
			days_until_due=obj.days_until_due,
			trial_period_days=obj.trial_period_days,
			metadata={'entity_id': obj.entity_id}))

		trial_start = datetime.fromtimestamp(kwargs.pop('trial_start'))
		trial_end = datetime.fromtimestamp(kwargs.pop('trial_end'))

		trial_period_days = (trial_end - trial_start).days

		return cutils.call(StripeSubscription, **{
			**kwargs,
			'trial_period_days': trial_period_days,
			'created': datetime.fromtimestamp(kwargs.pop('created')),
			'start_date': datetime.fromtimestamp(kwargs.pop('start_date')),
			'trial_start': trial_start,
			'trial_end': trial_end,
			'entity_id': kwargs['metadata']['entity_id']
		})

	def json(self) -> dict[str, any]:
		_dict = self.__dict__.copy()
		_dict['metadata'] = {'entity_id': self.entity_id}
		_dict['created'] = self.created.timestamp()
		return _dict

	def parse(self, kwargs) -> Subscription:
		pass


@traced
class PaymentStripe(PaymentService):

	def __init__(self, api_key: str):
		stripe.api_key = api_key
		self.page_limit = 100
		self.tries_before_fail = 30
		self.sleep_before_next_trie = 2

	""" CUSTOMER """

	def create_customer(self, customer: StripeCustomer) -> Customer | None:
		old_customer = self.get_customer(customer.entity_id, with_tries=False)

		if old_customer is not None:
			return old_customer

		try:
			return StripeCustomer.create(customer)
		except stripe.error.InvalidRequestError as err:
			return None

	def list_customers(self) -> list[Customer]:
		all_customers = []

		starting_after = None
		while True:
			customers: stripe.Customer = stripe.Customer.list(limit=self.page_limit, starting_after=starting_after)
			all_customers += customers.data
			if customers.has_more:
				starting_after = customers[-1].id
			else:
				break

		return [StripeCustomer.parse(**dict(c)) for c in all_customers]

	def get_customer(self, entity_id: str, with_tries: bool = True) -> Customer | None:
		tries = self.tries_before_fail if with_tries else 1

		while True:
			customers = self.search_customers(f"metadata['entity_id']:'{entity_id}'")
			tries -= 1

			if len(customers) == 0 and tries <= 0:
				return None
			elif len(customers) == 1:
				return customers[0]
			elif len(customers) > 1:
				raise Exception(f"Customers with duplicated entity_id: {customers}")

			time.sleep(self.sleep_before_next_trie)

	def search_customers(self, query: str) -> list[Customer]:
		return [StripeCustomer.parse(**dict(c)) for c in stripe.Customer.search(query=query, limit=self.page_limit).data]

	def delete_customer(self, entity_id: str, with_tries: bool = True) -> bool:
		customer = self.get_customer(entity_id=entity_id, with_tries=with_tries)

		if customer is None:
			return False

		tries = self.tries_before_fail

		while True:
			try:
				return stripe.Customer.delete(sid=customer.id).deleted
			except stripe.error.InvalidRequestError as err:
				pass

			tries -= 1
			if tries == 0:
				return False
			time.sleep(1)

	""" SUBSCRIPTION """

	def cancel_subscription(self, entity_id: str) -> bool:
		subscription = self.get_subscription(entity_id=entity_id)

		if subscription is None:
			return False

		try:
			return stripe.Subscription.delete(sid=subscription.id).deleted
		except stripe.error.InvalidRequestError as err:
			return False

	def update_subscription(self) -> Subscription | None:
		pass

	def list_subscription(self) -> list[Subscription]:
		all_subscriptions = []

		starting_after = None
		while True:
			subscriptions: stripe.Subscription = stripe.Subscription.list(limit=self.page_limit, starting_after=starting_after)
			all_subscriptions += subscriptions.data
			if subscriptions.has_more:
				starting_after = subscriptions[-1].id
			else:
				break

		return [StripeSubscription.parse(**dict(c)) for c in all_subscriptions]

	def get_subscription(self, entity_id: str) -> Subscription | None:
		subscriptions = self.search_subscription(f"metadata['entity_id']:'{entity_id}'")
		if len(subscriptions) == 0:
			return None
		elif len(subscriptions) == 1:
			return subscriptions[0]
		elif len(subscriptions) > 1:
			raise Exception(f"Customers with duplicated entity_id: {subscriptions}")

	def search_subscription(self, query: str) -> list[Subscription]:
		return [StripeSubscription.parse(**dict(s)) for s in stripe.Subscription.search(query=query, limit=self.page_limit).data]

	def create_subscription(self, subscription: Subscription):
		old_subscription = self.get_subscription(subscription.entity_id)

		if old_subscription is not None:
			return old_subscription

		try:
			return StripeSubscription.create(subscription)
		except stripe.error.InvalidRequestError as err:
			print(err)
			return None
