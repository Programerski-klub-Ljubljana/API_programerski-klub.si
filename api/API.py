# MIDLE WARE
import logging
import sys

from autologging import traced
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_utils.timing import add_timing_middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from api import const, autils
from api.routes import db, forms, auth
from app import APP
from core import cutils

log = logging.getLogger(__name__)

this = sys.modules[__name__]
inited: bool = False
fapi = FastAPI(**const.fastapi)


@traced
@fapi.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
	return JSONResponse(
		status_code=400,
		content={"error": str(exc)},
	)


@traced
def custom_openapi():
	if fapi.openapi_schema:
		return fapi.openapi_schema
	kwargs = cutils.filter_dict(get_openapi, fapi.__dict__)
	kwargs['routes'] = fapi.routes
	fapi.openapi_schema = autils.openapi(get_openapi(**kwargs))
	return fapi.openapi_schema


@traced
def init():
	if this.inited:
		log.warning('API already inited!')
		return

	APP.init(seed=True)

	# TIMING RESPONSES
	add_timing_middleware(fapi, record=log.info)

	# CORS
	fapi.add_middleware(CORSMiddleware, **const.cors)

	# ROUTES REGISTER
	fapi.include_router(db.router)
	fapi.include_router(forms.router)
	fapi.include_router(auth.router)

	# SETUP CUSTOM OPENAPI
	fapi.openapi = custom_openapi

	# IS INITED
	this.inited = True


__all__ = ['fapi', 'init']
