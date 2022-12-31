from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core import cutils


class SubscriptionHistoryStatus(str, Enum):
	WAS_SUBSCRIBED = "WAS_SUBSCRIBED"
	IS_SUBSCRIBED = "IS_SUBSCRIBED"
	NEVER_SUBSCRIBED = "NEVER_SUBSCRIBED"


class SubscriptionStatus(str, Enum):
	INCOMPLETE = 'incomplete'
	INCOMPLETE_EXPIRED = 'incomplete_expired'
	TRIALING = 'trialing'
	ACTIVE = 'active'
	PAST_DUE = 'past_due'
	CANCELED = 'canceled'
	UNPAID = 'unpaid'


class CollectionMethod(str, Enum):
	CHARGE_AUTOMATICALLY = 'charge_automatically'
	SEND_INVOICE = 'send_invoice'


@dataclass
class Customer:
	name: str
	billing_email: str
	subscriptions: list['Subscription'] = cutils.list_field()

	description: str = None
	id: str = None
	balance: int = None
	discount: str = None
	delinquent: bool = None
	created: datetime = None
	languages: list[str] = None

	deleted: bool = False

	def subscription_history_status(self, price: str) -> SubscriptionHistoryStatus:
		status = SubscriptionHistoryStatus.NEVER_SUBSCRIBED
		for sub in self.subscriptions:
			if price in sub.prices:
				status = SubscriptionHistoryStatus.WAS_SUBSCRIBED
				if sub.status != SubscriptionStatus.CANCELED:
					return SubscriptionHistoryStatus.IS_SUBSCRIBED

		return status


@dataclass
class Subscription:
	prices: list[str]
	customer: Customer | str
	collection_method: CollectionMethod
	days_until_due: int
	trial_period_days: int

	description: str = None
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
