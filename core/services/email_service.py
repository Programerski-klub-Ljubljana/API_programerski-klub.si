from abc import abstractmethod, ABC

from core.services.utils import Validation


class EmailService(ABC):
	@abstractmethod
	def obstaja(self, email) -> Validation:
		pass

	@abstractmethod
	def poslji(self):
		pass
