from abc import abstractmethod, ABC


class EmailService(ABC):
	@abstractmethod
	def obstaja(self, email) -> bool:
		pass

	@abstractmethod
	def poslji(self):
		pass
