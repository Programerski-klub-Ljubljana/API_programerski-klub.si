from abc import abstractmethod, ABC

from autologging import traced


@traced
class SmsService(ABC):
	@abstractmethod
	def obstaja(self, phone: str) -> bool:
		"""
		Must put phone with country code inside: +386
		"""
		pass
