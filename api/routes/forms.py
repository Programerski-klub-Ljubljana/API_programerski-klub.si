from datetime import date, datetime

from autologging import traced
from fastapi import Form
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from api import autils
from app import APP, CONST
from core import cutils
from core.domain.arhitektura_kluba import Clan, Kontakt, TipKontakta
from core.use_cases.validation_cases import Validate_kontakt

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
	val_kontakt: Validate_kontakt = APP.useCases.validate_kontakt()

	clan_kontakt = Kontakt(
		ime=ime, priimek=priimek, tip=TipKontakta.CLAN,
		email=[email], telefon=[telefon])

	skrbnik_kontakt = Kontakt(
		ime=ime_skrbnika, priimek=priimek_skrbnika, tip=TipKontakta.SKRBNIK,
		email=[email_skrbnika], telefon=[telefon_skrbnika])

	clan = Clan(
		ime=ime, priimek=priimek,
		rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva),
		geslo='geslo', dovoljenja=[],
		kontakt=[clan_kontakt],
		skrbniki=[skrbnik_kontakt],
		vpisi=[datetime.utcnow()]
	)

	validacije = val_kontakt.invoke(kontakt=clan_kontakt)
	if clan.mladoletnik:
		validacije += val_kontakt.invoke(kontakt=skrbnik_kontakt)

	pass_vals = list(filter(lambda x: x.ok, validacije))
	fail_vals = list(filter(lambda x: not x.ok, validacije))

	if len(pass_vals) == 0:
		client = {
			'IP.....': request.client.host,
			'PORT...': request.client.port,
			'USER...': request.headers['user-agent']}
		return templates.TemplateResponse("forms_prekrsek.html", {"request": request, 'client': client})
	elif len(fail_vals) > 0:
		napake = [val.data for val in fail_vals]
		return templates.TemplateResponse("forms_napaka.html", {"request": request, 'napake': napake, **locals()})

	html = templates.get_template('forms_vpis.html').render(locals())
	await APP.services.email.send(
		recipients=[email] + ([email_skrbnika] if otrok else []),
		subject=const.forms.vpis.subject,
		vsebina=html
	)

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
