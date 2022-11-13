import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi_utils.timing import add_timing_middleware

from api import const
from core import utils
from api.routes import db, forms, user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MIDLE WARE
app = FastAPI(**const.fastapi)


def custom_openapi():
	if app.openapi_schema:
		return app.openapi_schema
	kwargs = utils.filter_dict(get_openapi, app.__dict__)
	kwargs['routes'] = app.routes
	app.openapi_schema = utils.openapi(get_openapi(**kwargs))
	return app.openapi_schema


def init():
	# TIMING RESPONSES
	add_timing_middleware(app, record=logger.info, prefix="app", exclude="untimed")

	# CORS
	app.add_middleware(CORSMiddleware, **const.cors)

	# ROUTES REGISTER
	app.include_router(db.router)
	app.include_router(forms.router)
	app.include_router(user.router)

	# SETUP CUSTOM OPENAPI
	app.openapi = custom_openapi
