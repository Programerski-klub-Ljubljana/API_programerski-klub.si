import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi_utils.timing import add_timing_middleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from api import const, autils
from api.routes import db, forms, auth
from core import cutils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MIDLE WARE
api = FastAPI(**const.fastapi)


@api.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
	return JSONResponse(
		status_code=400,
		content={"error": str(exc)},
	)


def custom_openapi():
	if api.openapi_schema:
		return api.openapi_schema
	kwargs = cutils.filter_dict(get_openapi, api.__dict__)
	kwargs['routes'] = api.routes
	api.openapi_schema = autils.openapi(get_openapi(**kwargs))
	return api.openapi_schema


def init():
	# TIMING RESPONSES
	add_timing_middleware(api, record=logger.info, prefix="services_tests", exclude="untimed")

	# CORS
	api.add_middleware(CORSMiddleware, **const.cors)

	# ROUTES REGISTER
	api.include_router(db.router)
	api.include_router(forms.router)
	api.include_router(auth.router)

	# SETUP CUSTOM OPENAPI
	api.openapi = custom_openapi
