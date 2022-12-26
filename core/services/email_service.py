from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass
class EmailPerson:
	name: str = None
	email: str = None

	@staticmethod
	@abstractmethod
	def parse(data):
		pass


@dataclass
class Email:
	sender: EmailPerson = None
	subject: str = None
	content: str = None


class EmailService(ABC):
	@abstractmethod
	def check_existance(self, email: str) -> bool:
		pass

	@abstractmethod
	def send(self, recipients: list[str], subject: str, vsebina: str):
		pass

	@abstractmethod
	def mailbox(self) -> list[Email]:
		pass
