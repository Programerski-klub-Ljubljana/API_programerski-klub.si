from abc import abstractmethod, ABC
from dataclasses import dataclass

from autologging import traced


@traced
class TemplateA(ABC):
	@abstractmethod
	def __call__(self, key, value):
		pass

	@abstractmethod
	def __getattr__(self, item):
		pass


@traced
class TemplateService(ABC):
	@abstractmethod
	def init(self, **kwargs) -> TemplateA:
		pass
