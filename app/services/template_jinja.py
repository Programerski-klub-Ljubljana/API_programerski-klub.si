import jinja2
from autologging import traced

from core.services.template_service import TemplateService, TemplateA


class Template(TemplateA):
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

	def init(self, **kwargs):
		return Template(self.env, **kwargs)
