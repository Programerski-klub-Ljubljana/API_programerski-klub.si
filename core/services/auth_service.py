from abc import abstractmethod, ABC


class AuthService(ABC):
	@abstractmethod
	def authenticate(self):
		print('placilo')
