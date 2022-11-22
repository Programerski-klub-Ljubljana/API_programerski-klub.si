import copy

from autologging import traced
from fastapi import Form
from starlette.responses import HTMLResponse

from api import autils
from app import APP
from core.services.template_service import TemplateService
from core.use_cases.forms_vpis import Forms_vpis, TipProblema

router = autils.router(__name__)


@traced
@router.post("/vpis", response_class=HTMLResponse)
async def vpis(
		ime: str = Form(), priimek: str = Form(),
		dan_rojstva: int = Form(), mesec_rojstva: int = Form(), leto_rojstva: int = Form(),
		email: str = Form(), telefon: str = Form(),
		ime_skrbnika: str | None = Form(None), priimek_skrbnika: str | None = Form(None),
		email_skrbnika: str | None = Form(None), telefon_skrbnika: str | None = Form(None)):
	# TODO: Validiraj skrbnika v primeru ce kdo dela post requeste mimo web/a
	kwargs = copy.copy(locals())

	forms_vpis: Forms_vpis = APP.useCases.forms_vpis()
	template: TemplateService = APP.services.template()
	vpis = await forms_vpis.invoke(**kwargs)
	print(vpis)

	temp = template.init(**kwargs)
	if TipProblema.HACKER in vpis.razlogi_prekinitve:
		return HTMLResponse(content=temp.warn_prekrsek, status_code=400)
	elif TipProblema.NAPAKE in vpis.razlogi_prekinitve:
		temp.napake = [k.data for k in vpis.napacni_podatki_skrbnika + vpis.napacni_podatki_clana]
		return HTMLResponse(content=temp.warn_napaka, status_code=400)
	elif TipProblema.CHUCK_NORIS in vpis.razlogi_prekinitve:
		return HTMLResponse(content=temp.warn_chuck_noris)

	# POSILJANJE POTRDITVENEGA EMAILA
	return HTMLResponse(content=temp.ok_sprejeto, status_code=200)


@traced
@router.post("/izpis")
def izpis():
	return {}


@traced
@router.post('/kontakt')
def kontakt():
	return {'kontakt': True}
