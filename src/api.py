import logging

from fastapi import FastAPI
from fastapi_utils.timing import add_timing_middleware

from src.routes import db, payments, forms, user


def error(exception) -> dict:
	return {'error': str(exception)}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# MIDLE WARE
add_timing_middleware(app, record=logger.info, prefix="app", exclude="untimed")

# ROUTES REGISTER
app.include_router(db.router, prefix='/db')
app.include_router(forms.router, prefix='/forms')
app.include_router(payments.router, prefix='/payments')
app.include_router(user.router, prefix='/user')
