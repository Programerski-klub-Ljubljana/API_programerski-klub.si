from datetime import date

from fastapi import APIRouter, Form
from starlette.templating import Jinja2Templates

from src.db import Transaction
from src.domain.arhitektura_kluba import Clan, Kontakt, TipKontakta
from src.domain.oznanila_sporocanja import Sporocilo, TipSporocila
from src.services import email as EMAIL

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/vpis")
async def vpis_clan(
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
	html = templates.get_template('email_vpis.html').render(locals())
	await EMAIL.send(
		recipients=['jar.fmf@gmail.com'],
		subject="Programerski Klub Ljubljana | Potrdilo ob vpisu",
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

		return locals()


@router.post("/izpis")
def izpis():
	return {}


@router.post('/kontakt')
def kontakt():
	return {'kontakt': True}
