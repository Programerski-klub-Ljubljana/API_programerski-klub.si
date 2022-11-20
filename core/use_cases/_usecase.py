from abc import abstractmethod, ABC


class UseCase(ABC):
	@abstractmethod
	def invoke(self, *args, **kwargs):
		pass
