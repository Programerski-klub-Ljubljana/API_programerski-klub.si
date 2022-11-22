import copy
import logging
from datetime import datetime

from autologging import traced
from fastapi import Form
from starlette.responses import HTMLResponse

from api import autils
from app import APP
from core.services.template_service import TemplateService
from core.use_cases.forms_vpis import Forms_vpis, TipProblema, StatusVpisa

router = autils.router(__name__)
log = logging.getLogger(__name__)


@traced
@router.post("/vpis", response_class=HTMLResponse)
async def vpis(
		ime: str = Form(min_length=2), priimek: str = Form(min_length=2),
		dan_rojstva: int = Form(ge=1, le=31), mesec_rojstva: int = Form(ge=1, le=12),
		leto_rojstva: int = Form(ge=datetime.utcnow().year - 120, le=datetime.utcnow().year),
		email: str = Form(min_length=3), telefon: str = Form(min_length=4),
		ime_skrbnika: str | None = Form(None, min_length=2), priimek_skrbnika: str | None = Form(None, min_length=2),
		email_skrbnika: str | None = Form(None, min_length=3), telefon_skrbnika: str | None = Form(None, min_length=3)):
	kwargs = copy.copy(locals())

	forms_vpis: Forms_vpis = APP.useCases.forms_vpis()
	template: TemplateService = APP.services.template()

	status: StatusVpisa = await forms_vpis.invoke(**kwargs)
	log.info(status)

	temp = template.init(**{**kwargs, **{'kontakti': [k.data for k in status.validirani_podatki]}})
	if TipProblema.HACKER in status.razlogi_prekinitve:
		return HTMLResponse(content=temp.warn_prekrsek, status_code=400)
	elif TipProblema.NAPAKE in status.razlogi_prekinitve:
		temp.napake = [k.data for k in status.napacni_podatki_skrbnika + status.napacni_podatki_clana]
		return HTMLResponse(content=temp.warn_napaka, status_code=400)
	elif TipProblema.CHUCK_NORIS in status.razlogi_prekinitve:
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
