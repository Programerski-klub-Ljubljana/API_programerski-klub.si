from abc import abstractmethod, ABC

from core.services._utils import Validation


class SmsService(ABC):
	@abstractmethod
	def obstaja(self, phone: str) -> bool:
		"""
		Must put phone with country code inside: +386
		"""
		pass
