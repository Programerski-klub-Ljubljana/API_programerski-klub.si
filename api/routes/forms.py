from datetime import date

from autologging import traced
from fastapi import Form
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from api import const, autils
from core import cutils
from core.domain.arhitektura_kluba import Clan, Kontakt, TipKontakta
from core.domain.oznanila_sporocanja import Sporocilo, TipSporocila

router = autils.router(__name__)
templates = Jinja2Templates(directory=cutils.root_path("templates"))


@traced
@router.post("/vpis", response_class=HTMLResponse)
async def vpis(
		request: Request,
		ime: str = Form(),
		priimek: str = Form(),
		dan_rojstva: int = Form(),
		mesec_rojstva: int = Form(),
		leto_rojstva: int = Form(),
		email: str = Form(),
		telefon: str = Form(),

		ime_skrbnika: str = Form(None),
		priimek_skrbnika: str = Form(None),
		email_skrbnika: str = Form(None),
		telefon_skrbnika: str = Form(None)):
	age = cutils.age(leto_rojstva, mesec_rojstva, dan_rojstva)
	otrok = False
	validation = [(EMAIL.exist, email),
	              (TWILIO.exist, telefon)]

	if age < 18:
		otrok = True
		validation += [
			(TWILIO.exist, telefon_skrbnika),
			(EMAIL.exist, email_skrbnika)]

	NAPAKE = []
	GOOD_PERSON_SCORE = 0
	for validation_function, data in validation:
		if validation_function(data):
			GOOD_PERSON_SCORE += 1
		else:
			NAPAKE += [data]
	if GOOD_PERSON_SCORE <= 0:
		client = {
			'IP.....': request.client.host,
			'PORT...': request.client.port,
			'USER...': request.headers['user-agent']
		}
		return templates.TemplateResponse("forms_prekrsek.html", {"request": request, 'client': client})
	elif len(NAPAKE) > 0:
		return templates.TemplateResponse("forms_napaka.html", {"request": request, 'napake': NAPAKE, **locals()})

	html = templates.get_template('forms_vpis.html').render(locals())
	await EMAIL.send(
		recipients=[email] + ([email_skrbnika] if otrok else []),
		subject=const.forms.vpis.subject,
		vsebina=html
	)

	with Transaction() as root:
		skrbnik = Kontakt(
			ime=ime_skrbnika,
			priimek=priimek_skrbnika,
			tip=TipKontakta.SKRBNIK,
			email=email_skrbnika,
			telefon=telefon_skrbnika)

		clan = Clan(
			ime=ime,
			priimek=priimek,
			rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva),
			email=email,
			telefon=telefon,
			skrbniki=[skrbnik],
			vpisi=[date.today()])

		sporocilo = Sporocilo(
			tip=TipSporocila.FORMS_VPIS,
			vsebina=html)

		clan.povezi(sporocilo)
		root.save(clan, skrbnik, sporocilo)

	kwargs = {"request": request, **locals()}
	kwargs["sporocilo"] = const.forms.vpis.msg
	return templates.TemplateResponse("forms_success.html", kwargs)


@traced
@router.post("/izpis")
def izpis():
	return {}


@traced
@router.post('/kontakt')
def kontakt():
	return {'kontakt': True}
