from abc import abstractmethod, ABC

from core.services.utils import Validation


class SmsService(ABC):
	@abstractmethod
	def obstaja(self, phone: str) -> Validation:
		"""
		Must put phone with country code inside: +386
		"""
		pass

	@abstractmethod
	def poslji(self):
		pass
