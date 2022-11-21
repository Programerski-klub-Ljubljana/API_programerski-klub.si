import copy

from autologging import traced
from fastapi import Form
from starlette.responses import HTMLResponse

from api import autils
from app import APP
from core.services.template_service import TemplateService
from core.use_cases.forms_vpis import Forms_vpis

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
	validations = await forms_vpis.invoke(**kwargs)

	err_vals = list(filter(lambda x: not x.ok, validations))
	ok_vals = list(filter(lambda x: x.ok, validations))

	temp = template.init(**kwargs)

	# TEST ZA NAPAKE
	if len(err_vals) > 0:
		if len(ok_vals) == 0:
			return HTMLResponse(content=temp.warn_prekrsek, status_code=400)

		# CE JE VSAJ ENA VALIDACIJA FAIL
		temp.napake = [val.podatek for val in err_vals]
		return HTMLResponse(content=temp.warn_napaka, status_code=400)

	# POSILJANJE POTRDITVENEGA EMAILA
	return HTMLResponse(content=temp.ok_sprejeto, status_code=200)


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
