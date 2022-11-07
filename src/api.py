from fastapi import APIRouter, Form

from src import utils
from src.services import email as EMAIL

router = APIRouter()


@router.post("/vpis/clan")
async def vpis_clan(
		ime: str = Form(),
		priimek: str = Form(),
		dan_rojstva: int = Form(),
		mesec_rojstva: int = Form(),
		leto_rojstva: int = Form(),
		email: str = Form(),
		telefon: str = Form(),

		ime_skrbnika: str = Form(),
		priimek_skrbnika: str = Form(),
		email_skrbnika: str = Form(),
		telefon_skrbnika: str = Form()):

	print(utils.age(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva))

	await EMAIL.send(
		recipients=['jar.fmf@gmail.com'],
		template="email_vpis.html",
		subject="Programerski Klub Ljubljana | Potrdilo ob vpisu",
		body=locals()
	)

	return locals()


@router.get("/izpis")
def izpis():
	return {}


@router.post('/kontakt')
def kontakt():
	return {'kontakt': True}
