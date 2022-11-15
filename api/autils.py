from fastapi import APIRouter

from api import const


def router(_name_) -> APIRouter:
	name = _name_.split('.')[-1]
	return APIRouter(prefix=f'/{name}', tags=[name])


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
