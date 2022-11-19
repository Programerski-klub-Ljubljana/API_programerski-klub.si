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
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases.validation_cases import Validate_kontakt
from templates.__temps import Templates

router = autils.router(__name__)
templates = Jinja2Templates(directory=cutils.root_path("templates"))


@traced
@router.post("/vpis", response_class=HTMLResponse)
async def vpis(
		request: Request,
		ime: str = Form(), priimek: str = Form(),
		dan_rojstva: int = Form(), mesec_rojstva: int = Form(), leto_rojstva: int = Form(),
		email: str = Form(), telefon: str = Form(),
		ime_skrbnika: str = Form(None), priimek_skrbnika: str = Form(None),
		email_skrbnika: str = Form(None), telefon_skrbnika: str = Form(None)):
	#
	# INIT TEMPLTATES
	temps = Templates(templates, request, **locals())

	# INIT SERVICES AND CASES
	phone_service: PhoneService = APP.services.phone()
	email_service: EmailService = APP.services.email()
	val_kontakt: Validate_kontakt = APP.useCases.validate_kontakt()

	# FORMAT PHONE
	telefon = phone_service.parse(phone=telefon)
	telefon_skrbnika = phone_service.parse(phone=telefon_skrbnika)

	# USTVARI ELEMENTE
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

	# VALIDACIJA ELEMENTOV
	validacije = val_kontakt.invoke(kontakt=clan_kontakt)
	if clan.mladoletnik:
		skrbnik_kontakt = Kontakt(
			ime=ime_skrbnika, priimek=priimek_skrbnika, tip=TipKontakta.SKRBNIK,
			email=[email_skrbnika], telefon=[telefon_skrbnika])

		clan.kontakti.append(skrbnik_kontakt)
		validacije += val_kontakt.invoke(kontakt=skrbnik_kontakt)

	# SEPARACIJA OPRAVLJENE/ERRORED VALIDACIJE
	pass_vals = list(filter(lambda x: x.ok, validacije))
	fail_vals = list(filter(lambda x: not x.ok, validacije))

	# CE NOBENA VALIDACIJA NI BILA USPEŠNO
	if len(pass_vals) == 0:
		return temps.warn_prekrsek

	# CE JE VSAJ ENA VALIDACIJA FAIL
	elif len(fail_vals) > 0:
		napake = [val.data for val in fail_vals]
		return temps.warn_napaka

	# VSE VALIDACIJE SO BILE OPRAVLJENE USPEŠNO
	await email_service.send(
		recipients=[email] + ([email_skrbnika] if clan.mladoletnik else []),
		subject=CONST.subject("Vpis v klub"),
		vsebina=temps.email_vpis)

	return temps.ok_sprejeto


@traced
@router.get("/vpis/{uporabnik")
def vpis_uporabnik(uporabnik: str):
	return {}


@traced
@router.post("/izpis")
def izpis():
	return {}


@traced
@router.post('/kontakt')
def kontakt():
	return {'kontakt': True}
