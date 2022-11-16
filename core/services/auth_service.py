from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Token:
	data: str
	type: str


class AuthService(ABC):

	@abstractmethod
	def encode(self, data: dict, expiration: timedelta) -> Token:
		pass

	@abstractmethod
	def decode(self, token: str):
		pass

	@abstractmethod
	def verify(self, password, hashed_password) -> bool:
		pass

	@abstractmethod
	def hash(self, password):
		pass
