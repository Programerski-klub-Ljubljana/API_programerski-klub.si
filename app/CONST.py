from core import cutils

version = '0.1.0'
klub = 'Programerski klub Ljubljana'
domain = 'programerski-klub.si'
email = f'info@{domain}'
web = f'http://{domain}'
web_api = f'{web}/api'
github = 'https://github.com/programerski-klub-ljubljana'
logo = "https://avatars.githubusercontent.com/u/105967036"

auth_token_life = 24  # 24ur
verification_token_life = 48  # 2 dni
auth_confirm_url = f'{web_api}/auth/confirm'
auth_report_url = f'{web_api}/auth/report'

phone_country_code = "SI"

openapi = {
	'version': version,
	'title': f"API - {klub}",
	'contact': {'email': email, 'web': web, 'github': github},
	'description': f"""
		API server ki ga uporablja {klub} za svoje delovanje.
		Notri se nahaja vse stvari za popolno avtomatizacijo kluba ter spletne strani
		na "{web}" naslovu. """.removeprefix('\t'),
	'servers': [
		{'url': 'http://localhost:8000', 'description': 'Development'},
		{'url': web_api, 'description': 'Production'}]
}

cors = {
	'allow_credentials': True,
	'allow_origins': ['http://localhost:5173', web_api],
	'allow_methods': ["*"],
	'allow_headers': ["*"],
}

templates = cutils.root_path('templates')


class subject:
	vpis = f'{klub} | Potrdilo ob vpisu'
	vpis_skrbnik = f'{klub} | Obvestilo skrbnika o vpisu'
