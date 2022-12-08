import copy
import logging
from datetime import datetime

from autologging import traced
from fastapi import Form
from starlette.responses import HTMLResponse

from api import autils
from app import APP
from core.services.template_service import TemplateService
from core.use_cases.zacni_vclanitveni_postopek import Zacni_vclanitveni_postopek, TipPrekinitveVpisa, StatusVpisa

router = autils.router(__name__)
log = logging.getLogger(__name__)


@traced
@router.post("/vpis", response_class=HTMLResponse)
async def vpis(
		ime: str = Form(min_length=2), priimek: str = Form(min_length=2),
		dan_rojstva: int = Form(ge=1, le=31), mesec_rojstva: int = Form(ge=1, le=12),
		leto_rojstva: int = Form(ge=datetime.now().year - 120, le=datetime.now().year),
		email: str = Form(min_length=3), telefon: str = Form(min_length=4),
		ime_skrbnika: str | None = Form(None, min_length=2), priimek_skrbnika: str | None = Form(None, min_length=2),
		email_skrbnika: str | None = Form(None, min_length=3), telefon_skrbnika: str | None = Form(None, min_length=3)):
	kwargs = copy.copy(locals())

	forms_vpis: Zacni_vclanitveni_postopek = APP.cases.zacni_vclanitveni_postopek()
	template: TemplateService = APP.services.template()

	status: StatusVpisa = await forms_vpis.exe(**kwargs)
	log.info(status)

	temp = template.init(**{**kwargs, **{'kontakti': [k.token_data for k in status.validirani_podatki]}})
	if TipPrekinitveVpisa.HACKER in status.razlogi_prekinitve:
		return HTMLResponse(content=temp.warn_prekrsek, status_code=400)
	elif TipPrekinitveVpisa.NAPAKE in status.razlogi_prekinitve:
		temp.napake = [k.token_data for k in status.napacni_podatki_skrbnika + status.napacni_podatki_clana]
		return HTMLResponse(content=temp.warn_napaka, status_code=400)
	elif TipPrekinitveVpisa.CHUCK_NORIS in status.razlogi_prekinitve:
		return HTMLResponse(content=temp.warn_chuck_noris)

	# POSILJANJE POTRDITVENEGA EMAILA
	return HTMLResponse(content=temp.web_vpis_sprejeto, status_code=200)


@traced
@router.post("/izpis")
def izpis():
	return {}


@traced
@router.post('/kontakt')
def kontakt():
	return {'kontakt': True}
