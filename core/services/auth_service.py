from abc import abstractmethod, ABC
from datetime import timedelta


class AuthService(ABC):

	@abstractmethod
	def encode(self, data: dict, expiration: timedelta):
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
