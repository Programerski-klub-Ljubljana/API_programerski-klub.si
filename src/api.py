from fastapi import APIRouter, Form

from src import db
from src import utils
from src.services import email as EMAIL
from src.utils import todict, is_iterable

router = APIRouter()


def error(exception) -> dict:
	return {'error': str(exception)}


def nested_path(data, value=None) -> object:
	if value is None:
		return data
	path = value.split("/")
	ref = data
	while path:
		element, path = path[0], path[1:]
		if is_iterable(ref):
			ref = ref[int(element)]
		else:
			ref = getattr(ref, element)
	return ref


@router.get("/db/{path:path}")
def db_table(path: str | None = None, page: int | None = 0):
	print(locals())
	try:
		with db.transaction() as root:
			result = nested_path(root, path)
			start = 10 * page
			end = 10 * (page + 1)
			result = result[start:end] if is_iterable(result) else result
			return todict(result, max_depth=3)
	except Exception as err:
		return error(err)


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

@router.get("/transaction")
def transaction():
	return {}


@router.get("/izpis")
def izpis():
	return {}


@router.post('/kontakt')
def kontakt():
	return {'kontakt': True}
