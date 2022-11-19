version = '0.1.0'
klub = 'Programerski klub Ljubljana'
domain = 'programerski-klub.si'
email = f'info@{domain}'
web = f'http://{domain}'
web_api = f'{web}/api'
github = 'https://github.com/programerski-klub-ljubljana'
logo = "https://avatars.githubusercontent.com/u/105967036"

phone_country_code = "SI"
token_life = 24

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

subject = lambda info: f'{klub} | {info}'
