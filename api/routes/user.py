from datetime import timedelta

from fastapi import Depends, HTTPException, Security
from fastapi.security import (
	OAuth2PasswordRequestForm,
)

from api import utils
from app import auth

router = utils.router(__name__)


@router.post("/login", response_model=AUTH.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
	user = AUTH.authenticate_user(AUTH.fake_users_db, form_data.username, form_data.password)
	if not user:
		raise HTTPException(status_code=400, detail="Incorrect username or password")
	access_token_expires = timedelta(minutes=AUTH.ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = AUTH.create_access_token(
		data={"sub": user.username, "scopes": form_data.scopes},
		expires_delta=access_token_expires,
	)
	return {"access_token": access_token, "token_type": "bearer"}


@router.get("/info", response_model=AUTH.User)
async def info(current_user: AUTH.User = Depends(AUTH.get_current_active_user)):
	return current_user


@router.get("/items")
async def items(current_user: AUTH.User = Security(AUTH.get_current_active_user, scopes=["items"])):
	return [{"item_id": "Foo", "owner": current_user.username}]


@router.get("/status")
async def status(current_user: AUTH.User = Depends(AUTH.get_current_user)):
	return {"status": "ok"}
