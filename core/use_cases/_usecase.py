from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass
class UseCase(ABC):
	@abstractmethod
	def exe(self, *args, **kwargs):
		pass
