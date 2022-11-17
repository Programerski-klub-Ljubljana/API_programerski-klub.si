from abc import abstractmethod, ABC


class EmailService(ABC):
	@abstractmethod
	def obstaja(self, email) -> bool:
		pass
