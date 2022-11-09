import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.timing import add_timing_middleware

from src import env
from src.db import seed
from src.routes import db, forms, user

env
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MIDLE WARE
app = FastAPI()

origins = [
	"http://localhost",
	"http://localhost:5173",
	"http://localhost:5174",
	"http://localhost:8080",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
add_timing_middleware(app, record=logger.info, prefix="app", exclude="untimed")

# ROUTES REGISTER
app.include_router(db.router, prefix='/db')
app.include_router(forms.router, prefix='/forms')
app.include_router(user.router, prefix='/user')

seed.init()

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
