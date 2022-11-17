from abc import abstractmethod, ABC


class PaymentService(ABC):
	@abstractmethod
	def placilo(self):
		print('placilo')
