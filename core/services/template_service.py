from abc import abstractmethod, ABC

from autologging import traced


@traced
class TemplateRenderer(ABC):
	@abstractmethod
	def __call__(self, key, value):
		pass

	@abstractmethod
	def __getattr__(self, item):
		pass


@traced
class TemplateService(ABC):
	@abstractmethod
	def init(self, **kwargs) -> TemplateRenderer:
		pass
