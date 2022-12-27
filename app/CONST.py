from datetime import timedelta

from core import cutils

""" VARS """
version = '0.1.0'
org_name = 'Programerski klub Ljubljana'
logo = "https://avatars.githubusercontent.com/u/105967036"

""" APP, API """
domain = 'programerski-klub.si'
web = f'https://{domain}'
web_api = f'{web}/api'

""" CONTACTS """


class emails:
	info = f'info@{domain}'
	api = f'api@{domain}'

	test_vcs_member = f'test@{domain}'
	test = f'test@{domain}'
	test2 = f'test2@{domain}'


class phones:
	api = f'+38651240885'
	info = f'051-240-885'
	test = f'051-240-885'
	test2 = f'051-240-885'


""" GITHUB """
github_org = org_name.lower().replace(' ', '-')
github = f'https://github.com/{github_org}'

""" AUTH """
auth_token_url = '/auth/login'
auth_token_life = timedelta(hours=24)
auth_verification_token_life = timedelta(minutes=10)
auth_verification_size = 4

auth_signout_url = f'{web_api}/auth/signout'
auth_ownership_url = f'{web_api}/auth/ownership'
auth_report_url = f'{web_api}/auth/report'

""" PHONE """
phone_default_country_code = "SI"

""" PAYMENT """
days_until_due = 7
trial_period_days = 7 * 4

""" API SETTINGS """
api_openapi = {
	'version': version,
	'title': f"API - {org_name}",
	'contact': {'email': emails.info, 'web': web, 'github': github},
	'description': f"""
		API server ki ga uporablja {org_name} za svoje delovanje.
		Notri se nahaja vse stvari za popolno avtomatizacijo kluba ter spletne strani
		na "{web}" naslovu. """.removeprefix('\t'),
	'servers': [
		{'url': 'http://localhost:8000', 'description': 'Development'},
		{'url': web_api, 'description': 'Production'}]
}
api_cors = {
	'allow_credentials': True,
	'allow_origins': ['http://localhost:5173', web_api],
	'allow_methods': ["*"],
	'allow_headers': ["*"],
}
api_templates = cutils.root_path('templates')


class email_subject:
	vpis = f'{org_name} | Potrdilo ob vpisu'
	vpis_skrbnik = f'{org_name} | Obvestilo skrbnika o vpisu'
	verifikacija = f'{org_name} | Verifikacija osebe'
	verifikacija_izpisa = f'{org_name} | Verifikacija izpisa'
	porocilo_napake = f'{org_name} | Poročilo napake'


class payment_prices:
	klubska_clanarina = 'klubska_clanarina'
