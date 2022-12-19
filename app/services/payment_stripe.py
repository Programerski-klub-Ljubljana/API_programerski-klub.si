import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import stripe
from autologging import traced

from core import cutils
from core.services.payment_service import PaymentService, Customer, Subscription, SubscriptionStatus

log = logging.getLogger(__name__)


# TODO: Fix problems with duplications!!!


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
	"""
	metadata.entity_id
	created
	"""

	@staticmethod
	def create(obj: Customer):
		return StripeCustomer.parse(**dict(stripe.Customer.create(
			name=obj.name, description=obj.description,
			phone=obj.phone, email=obj.email,
			metadata={'entity_id': obj.entity_id}
		)))

	@staticmethod
	def parse(**kwargs) -> Customer:
		return cutils.call(StripeCustomer, **{
			**kwargs,
			'entity_id': kwargs['metadata']['entity_id'],
			'created': datetime.fromtimestamp(kwargs['created'])
		})


class StripeSubscription(Subscription, StripeObj):
	"""
	metadata.entity_id
	created
	items
	collection_method
	trial_period_days
	"""

	@staticmethod
	def create(obj: Subscription):
		return StripeSubscription.parse(**dict(stripe.Subscription.create(
			description=obj.description,
			items=[{'price': price_id} for price_id in obj.prices],
			customer=obj.customer.id,
			collection_method=obj.collection_method.value,
			days_until_due=obj.days_until_due,
			trial_period_days=obj.trial_period_days,
			metadata={'entity_id': obj.entity_id}
		)))

	@staticmethod
	def parse(**kwargs) -> Subscription:
		kwargs['trial_period_days'] = 0
		if kwargs.get("trial_start", False):
			kwargs['trial_start'] = datetime.fromtimestamp(kwargs['trial_start'])
			kwargs['trial_end'] = datetime.fromtimestamp(kwargs['trial_end'])
			kwargs['trial_period_days'] = (kwargs['trial_end'] - kwargs['trial_start']).days

		kwargs = {
			**kwargs,
			'prices': [item['id'] for item in kwargs['items']],
			'created': datetime.fromtimestamp(kwargs['created']),
			'start_date': datetime.fromtimestamp(kwargs['start_date']),
			'entity_id': kwargs['metadata']['entity_id']
		}

		return cutils.call(StripeSubscription, **kwargs)


@traced
class PaymentStripe(PaymentService):
	tries_before_fail = 30
	tries_before_create = 3
	tries_before_delete = 3
	page_limit = 100
	sleep_before_next_try = 2

	def __init__(self, api_key: str):
		stripe.api_key = api_key

	""" CUSTOMER """

	def create_customer(self, customer: StripeCustomer) -> Customer | None:
		old_customer = self.get_customer(entity_id=customer.entity_id, delay=False, tries=self.tries_before_create)

		if old_customer is not None:
			log.warning("Customer allready exists")
			return None

		try:
			return StripeCustomer.create(customer)
		except stripe.error.InvalidRequestError as err:
			return None

	def get_customer(self, entity_id: str, delay: bool = False, tries: int = tries_before_fail) -> Customer | None:
		while True:
			customers = self.search_customers(f"metadata['entity_id']:'{entity_id}'")
			tries -= 1

			if len(customers) == 0 and tries < 0:
				return None
			elif len(customers) == 1:
				return customers[0]
			elif len(customers) > 1:
				raise Exception(f"Customers with duplicated entity_id: {customers}")

			if delay:
				time.sleep(self.sleep_before_next_try)

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

	def search_customers(self, query: str) -> list[Customer]:
		return [StripeCustomer.parse(**dict(c)) for c in stripe.Customer.search(query=query, limit=self.page_limit).data]

	def delete_customer(self, entity_id: str) -> bool:
		customer = self.get_customer(entity_id=entity_id, delay=False, tries=self.tries_before_delete)

		if customer is None:
			log.warning("Customer does not exists!")
			return False

		tries = self.tries_before_fail
		while True:
			try:
				return stripe.Customer.delete(sid=customer.id).deleted
			except stripe.error.InvalidRequestError as err:
				pass

			tries -= 1
			if tries <= 0:
				return False
			time.sleep(self.sleep_before_next_try)

	""" SUBSCRIPTION """

	def create_subscription(self, subscription: Subscription):
		old_subscription = self.get_subscription(entity_id=subscription.entity_id, delay=False, tries=self.tries_before_create)

		if old_subscription is not None:
			log.error("Subscription allready exists")
			return None

		try:
			return StripeSubscription.create(subscription)
		except stripe.error.InvalidRequestError as err:
			log.error(err)
			return None

	def get_subscription(self, entity_id: str, delay: bool = False, tries=tries_before_fail) -> Subscription | None:
		while True:
			subscriptions = self.search_subscription(f"metadata['entity_id']:'{entity_id}'")
			tries -= 1

			if len(subscriptions) == 0 and tries < 0:
				return None
			elif len(subscriptions) == 1:
				return subscriptions[0]
			elif len(subscriptions) > 1:
				raise Exception(f"Subscription with duplicated entity_id: {subscriptions}")

			if delay:
				time.sleep(self.sleep_before_next_try)

	def list_subscriptions(self) -> list[Subscription]:
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

	def search_subscription(self, query: str) -> list[Subscription]:
		return [StripeSubscription.parse(**dict(s)) for s in stripe.Subscription.search(query=query, limit=self.page_limit).data]

	def cancel_subscription(self, entity_id: str) -> bool:
		subscription = self.get_subscription(entity_id=entity_id, delay=False, tries=self.tries_before_delete)

		if subscription is None:
			log.warning("Subscription does not exists")
			return False

		tries = self.tries_before_fail
		while True:
			try:
				sub = stripe.Subscription.delete(sid=subscription.id)
				return sub.status == SubscriptionStatus.CANCELED.value
			except stripe.error.InvalidRequestError as err:
				log.error(err)
				pass

			tries -= 1
			if tries <= 0:
				return False
			time.sleep(self.sleep_before_next_try)
