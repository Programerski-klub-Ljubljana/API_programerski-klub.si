from datetime import date, datetime

from autologging import traced
from fastapi import Form
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from api import autils
from app import APP
from core import cutils
from core.domain.arhitektura_kluba import Clan, Kontakt, TipKontakta
from core.services.email_service import EmailService
from core.use_cases.validation_cases import Validate_kontakt
from templates import temp

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
	email_service: EmailService = APP.services.email()
	val_kontakt: Validate_kontakt = APP.useCases.validate_kontakt()

	clan_kontakt = Kontakt(
		ime=ime, priimek=priimek, tip=TipKontakta.CLAN,
		email=[email], telefon=[telefon])

	clan = Clan(
		ime=ime, priimek=priimek,
		rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva),
		geslo='geslo', dovoljenja=[],
		kontakti=[clan_kontakt],
		vpisi=[datetime.utcnow()]
	)

	validacije = val_kontakt.invoke(kontakt=clan_kontakt)
	if clan.mladoletnik:
		skrbnik_kontakt = Kontakt(
			ime=ime_skrbnika, priimek=priimek_skrbnika, tip=TipKontakta.SKRBNIK,
			email=[email_skrbnika], telefon=[telefon_skrbnika])

		clan.kontakti.append(skrbnik_kontakt)
		validacije += val_kontakt.invoke(kontakt=skrbnik_kontakt)

	pass_vals = list(filter(lambda x: x.ok, validacije))
	fail_vals = list(filter(lambda x: not x.ok, validacije))

	if len(pass_vals) == 0:
		return templates.TemplateResponse("forms_prekrsek.html", {"request": request})
	elif len(fail_vals) > 0:
		napake = [val.data for val in fail_vals]
		return templates.TemplateResponse("forms_napaka.html", {"request": request, 'napake': napake, **locals()})

	await email_service.send(
		recipients=[email] + ([email_skrbnika] if clan.mladoletnik else []),
		subject=forms.vpis.subject,
		vsebina=templates.get_template('forms_vpis.html').render(locals()))

	kwargs = {"request": request, **locals(), "sporocilo": forms.vpis.msg}
	return templates.TemplateResponse("forms_success.html", kwargs)


@traced
@router.post("/izpis")
def izpis():
	return {}


@traced
@router.post('/kontakt')
def kontakt():
	return {'kontakt': True}
