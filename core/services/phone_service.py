import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass

from autologging import traced

log = logging.getLogger(__name__)


class ERROR_PHONE_FORMAT(Exception):
	pass


@dataclass
class PhoneOrigin:
	languages: list[str]
	country: str | None
	name: str | None


@traced
class PhoneService(ABC):
	@abstractmethod
	def check_existance(self, phone: str) -> bool:
		pass

	@abstractmethod
	def origin(self, phone: str) -> PhoneOrigin:
		pass

	@abstractmethod
	def format(self, phone: str) -> str:
		pass

	@abstractmethod
	def send_sms(self, phone: str, text: str) -> bool:
		pass
