from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime
from enum import auto

from core.domain._enums import EntityEnum


@dataclass
class Customer:
	entity_id: str
	name: str
	description: str
	phone: str
	email: str
	default_source: str

	id: str = None
	balance: int = None
	discount: str = None
	delinquent: bool = None
	created: datetime = None


class SubscriptionStatus(EntityEnum):
	incomplete = auto()
	incomplete_expired = auto()
	trialing = auto()
	active = auto()
	past_due = auto()
	canceled = auto()
	unpaid = auto()


class CollectionMethod(EntityEnum):
	CHARGE_AUTOMATICALLY = 'charge_automatically'
	SEND_INVOICE = 'send_invoice'


@dataclass
class Subscription:
	entity_id: str
	description: str
	items: list[str]
	customer: Customer
	collection_method: CollectionMethod
	days_until_due: int
	trial_period_days: int

	id: str = None
	status: SubscriptionStatus = None
	currency: str = None

	start: datetime = None
	created: datetime = None
	trial_start: datetime = None
	trial_end: datetime = None

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
	def get_customer(self, entity_id: str, with_tries: bool = True) -> Customer | None:
		pass

	@abstractmethod
	def search_customers(self, query: str) -> list[Customer]:
		pass

	@abstractmethod
	def delete_customer(self, entity_id: str, with_tries: bool = True) -> bool:
		pass

	""" SUBSCRIPTION """

	@abstractmethod
	def create_subscription(self, subscription: Subscription) -> Subscription | None:
		pass

	@abstractmethod
	def update_subscription(self) -> Subscription | None:
		pass

	@abstractmethod
	def cancel_subscription(self) -> Subscription | None:
		pass

	@abstractmethod
	def list_subscription(self) -> list[Subscription]:
		pass

	@abstractmethod
	def search_subscription(self, query: str) -> list[Subscription]:
		pass

	@abstractmethod
	def delete_subscription(self) -> bool:
		pass
