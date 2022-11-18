from abc import abstractmethod, ABC


class EmailService(ABC):
	@abstractmethod
	def obstaja(self, email) -> bool:
		pass

	@abstractmethod
	def send(self, recipients: str, subject: str, vsebina: str):
		pass
