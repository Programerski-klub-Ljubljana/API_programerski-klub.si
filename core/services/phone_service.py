import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass

from autologging import traced
from countryinfo import CountryInfo

log = logging.getLogger(__name__)


@dataclass
class PhoneOrigin:
	timezone: str
	languages: list[str]
	country: str
	name: str


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

	def send_sms(self, phone: str, text: str) -> bool:
		pass
