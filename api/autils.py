from dataclasses import dataclass

from autologging import traced
from fastapi import APIRouter

from app import CONST

fastapi = {
	'version': const.version,
	'title': f"API - {const.klub}",
	'contact': {'email': const.email, 'web': const.web, 'github': const.github},
	'description': f"""
		API server ki ga uporablja {const.klub} za svoje delovanje.
		Notri se nahaja vse stvari za popolno avtomatizacijo kluba ter spletne strani
		na "{const.web}" naslovu. """.removeprefix('\t'),
	'servers': [
		{'url': 'http://localhost:8000', 'description': 'Development'},
		{'url': const.web_api, 'description': 'Production'}]
}

cors = {
	'allow_credentials': True,
	'allow_origins': ['http://localhost:5173', const.web_api],
	'allow_methods': ["*"],
	'allow_headers': ["*"],
}


@dataclass
@traced
class Form:
	subject: str
	msg: str

	def __post_init__(self):
		self.subject = f'{const.klub} | {self.subject}'


@dataclass
class forms:
	vpis = Form('Potrdilo ob vpisu', 'Preveri če si dobil potrditveni email.')


@traced
def router(_name_) -> APIRouter:
	name = _name_.split('.')[-1]
	return APIRouter(prefix=f'/{name}', tags=[name])


@traced
def openapi(data):
	translator = {}
	for path in data["paths"].values():
		for op in path.values():
			function_name = '_'.join(str(op['summary']).lower().split())
			tag = op['tags'][0].lower()
			translator[op['operationId']] = f'{tag}_{function_name}'
			op["operationId"] = function_name

	# FIXING SCHEMES
	schemas = data['components']['schemas']
	for old_name, new_name in translator.items():
		schemaKey = f'Body_{old_name}'
		if schemaKey in schemas:
			schemas[schemaKey]['title'] = new_name.replace('_', ' ').capitalize()
	data["info"]["x-logo"] = {"url": const.logo}
	return data
