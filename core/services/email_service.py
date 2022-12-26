from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass
class EmailPerson:
	name: str = None
	email: str = None

	@staticmethod
	@abstractmethod
	def parse(data):
		pass


class EmailFlag(str, Enum):
	SEEN = '\\Seen'
	ANSWERED = '\\Answered'
	FLAGGED = '\\Flagged'
	DELETED = '\\Deleted'
	DRAFT = '\\Draft'

	@classmethod
	def parse(cls, data):
		for finger in cls:
			if finger == data:
				return finger


@dataclass
class EmailFolderStatus:
	messages: int
	recent: int
	unseen: int


@dataclass
class Email:
	id: str = None
	sender: EmailPerson = None
	subject: str = None
	content: str = None
	created: datetime = None
	flags: list[str] = None


class EmailService(ABC):
	@abstractmethod
	def check_existance(self, email: str) -> bool:
		pass

	@abstractmethod
	def send(self, recipients: list[str], subject: str, vsebina: str):
		pass

	@abstractmethod
	def get_all(self) -> list[Email]:
		pass

	@abstractmethod
	def folder_status(self, folder: str) -> EmailFolderStatus:
		pass

	@abstractmethod
	def inbox_status(self) -> EmailFolderStatus:
		pass

	@abstractmethod
	def delete(self, id: str) -> bool:
		pass
