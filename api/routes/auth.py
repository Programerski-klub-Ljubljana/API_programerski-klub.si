from autologging import traced
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

from api import autils
from app import APP

router = autils.router(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class TokenResponse(BaseModel):
	access_token: str
	token_type: str


@traced
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
	login = APP.useCases.auth_login()
	token = login.invoke(username=form_data.username, password=form_data.password)

	if token is not None:
		return {'access_token': token.data, "token_type": token.type}

	raise HTTPException(
		status_code=HTTP_401_UNAUTHORIZED,
		detail="Incorrect username or password",
		headers={"WWW-Authenticate": "Bearer"},
	)


@traced
@router.get("/info")
def info(token: str = Depends(oauth2_scheme)):
	auth_info = APP.useCases.auth_info()
	return auth_info.invoke(token)




@traced
@router.get("/items")
def items():
	return [{"item_id": "Foo", "owner": 'current_user.username'}]


@traced
@router.get("/status")
def status():
	return {"status": "ok"}
