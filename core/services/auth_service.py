from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import timedelta, datetime


@dataclass
class Token:
	data: str
	type: str


@dataclass
class TokenData:
	username: str
	exp: datetime = None


class AuthService(ABC):

	@abstractmethod
	def encode(self, data: TokenData, expiration: timedelta) -> Token:
		pass

	@abstractmethod
	def decode(self, token: str) -> TokenData:
		pass

	@abstractmethod
	def verify(self, password, hashed_password) -> bool:
		pass

	@abstractmethod
	def hash(self, password):
		pass
