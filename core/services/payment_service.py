from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime

from core.domain._enums import EntityEnum


@dataclass
class Customer:
	name: str
	description: str
	phone: str
	email: str

	id: str = None
	balance: int = None
	discount: str = None
	delinquent: bool = None
	created: datetime = None

	deleted: bool = False


class SubscriptionStatus(EntityEnum):
	INCOMPLETE = 'incomplete'
	INCOMPLETE_EXPIRED = 'incomplete_expired'
	TRIALING = 'trialing'
	ACTIVE = 'active'
	PAST_DUE = 'past_due'
	CANCELED = 'canceled'
	UNPAID = 'unpaid'


class CollectionMethod(EntityEnum):
	CHARGE_AUTOMATICALLY = 'charge_automatically'
	SEND_INVOICE = 'send_invoice'


@dataclass
class Subscription:
	description: str
	prices: list[str]
	customer: Customer
	collection_method: CollectionMethod
	days_until_due: int
	trial_period_days: int

	id: str = None
	status: SubscriptionStatus = None
	currency: str = None

	start_date: datetime = None
	created: datetime = None
	trial_start: datetime = None
	trial_end: datetime = None
	canceled_at: datetime = None


# add_invoice_items
# pending_invoice_item_interval


class PaymentService(ABC):
	""" CUSTOMER """

	@abstractmethod
	def create_customer(self, customer: Customer) -> Customer | None:
		pass

	@abstractmethod
	def list_customers(self) -> list[Customer]:
		pass

	@abstractmethod
	def get_customer(self, id: str) -> Customer | None:
		pass

	@abstractmethod
	def search_customers(self, query: str) -> list[Customer]:
		pass

	@abstractmethod
	def delete_customer(self, id: str) -> bool:
		pass

	""" SUBSCRIPTION """

	@abstractmethod
	def create_subscription(self, subscription: Subscription) -> Subscription | None:
		pass

	@abstractmethod
	def get_subscription(self, id: str) -> Subscription | None:
		pass

	@abstractmethod
	def list_subscriptions(self) -> list[Subscription]:
		pass

	@abstractmethod
	def search_subscription(self, query: str) -> list[Subscription]:
		pass

	@abstractmethod
	def cancel_subscription(self, id: str) -> bool:
		pass
