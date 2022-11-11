import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.timing import add_timing_middleware

from src import utils
from src.routes import db, forms, user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MIDLE WARE
app = FastAPI(
	version='0.1.0',
	title="API Programerskega kluba Ljubljana",
	contact={
		'email': 'info@programerski-klub.si',
		'web': 'http://programerski-klub.si',
		'github': 'https://github.com/programerski-klub-ljubljana'
	},
	description="""
		API server ki ga uporablja Programerski klub Ljubljana za svoje delovanje.
		Notri se nahaja vse stvari za popolno avtomatizacijo kluba ter spletne strani
		na "https://rogramerski-klub.si" naslovu.
	""".removeprefix('\t'),
	servers=[
		{'url': 'http://localhost:8000', 'description': 'Development'},
		{'url': 'https://programerski-klub.si/api', 'description': 'Production'}
	]
)


@app.get('/schema', include_in_schema=False)
def openapi():
	return utils.openapi(app.openapi())


def init():
	# TIMING RESPONSES
	add_timing_middleware(app, record=logger.info, prefix="app", exclude="untimed")

	# CORS
	app.add_middleware(
		CORSMiddleware,
		allow_credentials=True,
		allow_origins=['http://localhost'],
		allow_methods=["*"],
		allow_headers=["*"])

	# ROUTES REGISTER
	app.include_router(db.router)
	app.include_router(forms.router)
	app.include_router(user.router)
