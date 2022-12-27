from abc import abstractmethod, ABC

from autologging import traced


@traced
class TemplateRenderer(ABC):
	@abstractmethod
	def set(self, **kwargs):
		pass

	@abstractmethod
	def __getattr__(self, item) -> str:
		pass


@traced
class TemplateService(ABC):
	@abstractmethod
	def init(self, **kwargs) -> TemplateRenderer:
		pass
