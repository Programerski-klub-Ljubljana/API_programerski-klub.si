import jinja2
from autologging import traced

from app import CONST
from core.services.template_service import TemplateService, TemplateRenderer


class TemplateRendererJinja(TemplateRenderer):
	def __init__(self, env, **kwargs):
		self.env = env
		self.kwargs = kwargs

	def __call__(self, key, value):
		self.kwargs[key] = value

	def __getattr__(self, item):
		template = self.env.get_template(f'{item}.html')
		return template.render(**self.kwargs)


@traced
class TemplateJinja(TemplateService):
	def __init__(self, searchpath: str):
		self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=searchpath))
		self.kwargs = {}
		self.__init()

	def __init(self):
		for ele, val in CONST.__dict__.items():
			if isinstance(val, str | float | int):
				self.kwargs[f'CONST_{ele}'] = val

	def init(self, **kwargs):
		return TemplateRendererJinja(self.env, **{**kwargs, **self.kwargs})
