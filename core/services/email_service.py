from abc import abstractmethod, ABC


class EmailService(ABC):
	@abstractmethod
	def check_existance(self, email: str) -> bool:
		pass

	@abstractmethod
	def send(self, recipients: list[str], subject: str, vsebina: str):
		pass
