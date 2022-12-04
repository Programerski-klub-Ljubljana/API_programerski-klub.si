from abc import abstractmethod, ABC


class PaymentService(ABC):
	@abstractmethod
	def create_customer(self, entity_id: str, full_name, email: str, phone: str):
		pass

	@abstractmethod
	def delete_customer(self, email: str):
		pass

	@abstractmethod
	def list_customers(self, email: str):
		pass

	@abstractmethod
	def search_customer(self, query: str):
		pass
