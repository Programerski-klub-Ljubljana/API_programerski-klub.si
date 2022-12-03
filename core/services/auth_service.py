from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import timedelta, datetime


@dataclass
class Token:
	data: str
	type: str


class TokenData:
	def __init__(self, data: str | None):
		self.d = data
		self.exp: datetime | None = None

	@staticmethod
	def from_token(**kwargs):
		t = TokenData(data=None)
		for k, v in kwargs.items():
			setattr(t, k, v)
		return t


class AuthService(ABC):

	@abstractmethod
	def encode(self, token_data: TokenData, expiration: timedelta) -> Token:
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
