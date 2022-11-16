from abc import abstractmethod, ABC

from autologging import traced


@traced
class EmailService(ABC):
	@abstractmethod
	def obstaja(self, email) -> bool:
		pass
