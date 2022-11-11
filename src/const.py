from dataclasses import dataclass

version = '0.1.0'
klub = 'Programerski klub Ljubljana'
email = 'info@programerski-klub.si'
web = 'http://programerski-klub.si'
web_api = f'{web}/api'
github = 'https://github.com/programerski-klub-ljubljana'
logo = "https://avatars.githubusercontent.com/u/105967036"

fastapi = {
	'version': version,
	'title': f"API - {klub}",
	'contact': {'email': email, 'web': web, 'github': github},
	'description': """
		API server ki ga uporablja Programerski klub Ljubljana za svoje delovanje.
		Notri se nahaja vse stvari za popolno avtomatizacijo kluba ter spletne strani
		na "https://rogramerski-klub.si" naslovu. """.removeprefix('\t'),
	'servers': [{'url': 'http://localhost:8000', 'description': 'Development'},
	            {'url': web_api, 'description': 'Production'}]
}

cors = {
	'allow_credentials': True,
	'allow_origins': ['http://localhost:5173', web_api],
	'allow_methods': ["*"],
	'allow_headers': ["*"],
}


@dataclass
class Form:
	subject: str
	msg: str

	def __post_init__(self):
		self.subject = f'{klub} | {self.subject}'


@dataclass
class forms:
	vpis = Form('Potrdilo ob vpisu', 'Preveri če si dobil potrditveni email.')
