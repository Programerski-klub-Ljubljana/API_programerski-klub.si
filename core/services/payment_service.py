from abc import abstractmethod, ABC

from autologging import traced


@traced
class PaymentService(ABC):
	@abstractmethod
	def placilo(self):
		print('placilo')
