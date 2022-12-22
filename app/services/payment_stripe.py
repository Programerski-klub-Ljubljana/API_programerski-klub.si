import logging
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
			email=obj.billing_email,
			preferred_locales=obj.languages,
		)))

	@staticmethod
	def parse(**kwargs) -> Customer:
		return cutils.call(StripeCustomer, **{
			**kwargs,
			'billing_email': kwargs['email'],
			'deleted': kwargs.get('deleted', False),
			'created': datetime.fromtimestamp(kwargs.get('created', None)),
			'languages': kwargs.get('preferred_locales', [])
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
			expand=['customer'],
		)))

	@staticmethod
	def parse(**kwargs) -> Subscription:
		kwargs['trial_period_days'] = 0
		if kwargs.get("trial_start", False):
			kwargs['trial_start'] = datetime.fromtimestamp(kwargs['trial_start'])
			kwargs['trial_end'] = datetime.fromtimestamp(kwargs['trial_end'])
			kwargs['trial_period_days'] = (kwargs['trial_end'] - kwargs['trial_start']).days
		canceled_at = kwargs['canceled_at']
		kwargs = {
			**kwargs,
			'customer': StripeCustomer.parse(**kwargs['customer']),
			'prices': [item['id'] for item in kwargs['items']],
			'created': datetime.fromtimestamp(kwargs['created']),
			'start_date': datetime.fromtimestamp(kwargs['start_date']),
			'canceled_at': None if canceled_at is None else datetime.fromtimestamp(canceled_at)
		}

		return cutils.call(StripeSubscription, **kwargs)


def stripe_request(default_value):
	def decorator(function):
		def wrapper(*args, **kwargs):
			try:
				return function(*args, **kwargs)
			except stripe.error.InvalidRequestError as err:
				log.warning(err)
				return default_value

		return wrapper

	return decorator


@traced
class PaymentStripe(PaymentService):

	def __init__(self, api_key: str):
		stripe.api_key = api_key
		self.page_limit = 100

	""" CUSTOMER """

	@stripe_request(default_value=None)
	def create_customer(self, customer: StripeCustomer) -> Customer | None:
		return StripeCustomer.create(customer)

	@stripe_request(default_value=None)
	def get_customer(self, id: str) -> Customer | None:
		c = stripe.Customer.retrieve(id=id)
		if c.get('deleted', False):
			return None
		return StripeCustomer.parse(**c)

	def list_customers(self) -> list[Customer]:
		all_customers = []

		starting_after = None
		while True:
			customers: stripe.Customer = stripe.Customer.list(limit=self.page_limit, starting_after=starting_after)
			all_customers += customers.data
			if customers.has_more:
				starting_after = list(customers)[-1].id
			else:
				break

		return [StripeCustomer.parse(**dict(c)) for c in all_customers]

	def search_customers(self, query: str) -> list[Customer]:
		return [StripeCustomer.parse(**dict(c)) for c in stripe.Customer.search(query=query, limit=self.page_limit).data]

	@stripe_request(default_value=False)
	def delete_customer(self, id: str) -> bool:
		return stripe.Customer.delete(sid=id).deleted

	""" SUBSCRIPTION """

	@stripe_request(default_value=None)
	def create_subscription(self, subscription: Subscription):
		return StripeSubscription.create(subscription)

	@stripe_request(default_value=None)
	def get_subscription(self, id: str) -> Subscription | None:
		sub = stripe.Subscription.retrieve(id=id, expand=['customer'])
		return StripeSubscription.parse(**dict(sub))

	def list_subscriptions(self) -> list[Subscription]:
		all_subscriptions = []

		starting_after = None
		while True:
			subscriptions = stripe.Subscription.list(limit=self.page_limit, starting_after=starting_after, expand=['data.customer'])
			all_subscriptions += subscriptions.data
			if subscriptions.has_more:
				starting_after = subscriptions[-1].id
			else:
				break

		return [StripeSubscription.parse(**dict(c)) for c in all_subscriptions]

	def search_subscription(self, query: str) -> list[Subscription]:
		return [StripeSubscription.parse(**dict(s)) for s in stripe.Subscription.search(query=query, limit=self.page_limit, expand=['customer']).data]

	@stripe_request(default_value=False)
	def cancel_subscription(self, id: str) -> bool:
		sub = stripe.Subscription.delete(sid=id)
		return sub.status == SubscriptionStatus.CANCELED.value
