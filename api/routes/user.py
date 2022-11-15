from datetime import timedelta

from fastapi import Depends, HTTPException, Security
from fastapi.security import (
	OAuth2PasswordRequestForm,
)

from api import autils
from app.services.jwt_auth import *
from core.domain.arhitektura_kluba import Clan

router = autils.router(__name__)


@router.post("/login")
async def login():
	return {"access_token": 'access_token', "token_type": "bearer"}


@router.get("/info")
async def info():
	return 'current_user'


@router.get("/items")
async def items():
	return [{"item_id": "Foo", "owner": 'current_user.username'}]


@router.get("/status")
async def status():
	return {"status": "ok"}
