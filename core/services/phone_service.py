import logging
from abc import abstractmethod, ABC

from autologging import traced

log = logging.getLogger(__name__)


@traced
class PhoneService(ABC):
	@abstractmethod
	def obstaja(self, phone: str) -> bool:
		pass

	@abstractmethod
	def format(self, phone: str) -> str:
		pass

	def sms(self, phone: str, text: str) -> str:
		pass
