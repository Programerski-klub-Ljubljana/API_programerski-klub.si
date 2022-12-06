from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaymentCustomer:
	entity_id: str
	name: str
	description: str
	phone: str
	email: str

	id: str | None = None
	balance: int = 0
	discount: str = None
	delinquent: bool = False
	created: datetime = None


class PaymentService(ABC):
	@abstractmethod
	def create_customer(self, customer: PaymentCustomer) -> PaymentCustomer | None:
		pass

	@abstractmethod
	def list_customers(self) -> list[PaymentCustomer]:
		pass

	@abstractmethod
	def get_customer(self, entity_id: str, with_tries: bool = True) -> PaymentCustomer | None:
		pass

	@abstractmethod
	def search_customers(self, query: str) -> list[PaymentCustomer]:
		pass

	@abstractmethod
	def delete_customer(self, entity_id: str, with_tries: bool = True) -> bool:
		pass
