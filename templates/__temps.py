from dataclasses import dataclass

from autologging import traced
from starlette.requests import Request
from starlette.templating import _TemplateResponse, Jinja2Templates

from app import CONST


@dataclass
@traced
class Form:
	subject: str
	msg: str

	def __post_init__(self):
		self.subject = f'{CONST.klub} | {self.subject}'


vpis = Form('Potrdilo ob vpisu', 'Preveri če si dobil potrditveni email.')


class Templates:
	status = {
		'ok': 200,
		'warn': 400,
		'error': 500}

	def __init__(self, temps: Jinja2Templates, req: Request, **kwargs):
		self.temps = temps
		self.req = req
		self.kwargs = kwargs

	def template(self, status: int, name: str) -> _TemplateResponse:
		return self.temps.TemplateResponse(
			name=f'{name}.html',
			context={'request': self.req, **self.kwargs},
			status_code=status)

	def html(self, name: str):
		return self.temps.get_template(f'{name}.html').render(**self.kwargs)

	def __getattr__(self, item):
		res_type = item.split('_')[0]

		if res_type != 'email':
			status = self.status.get(res_type, 200)
			return self.template(status=status, name=item)
		else:
			return self.html(name=item)
