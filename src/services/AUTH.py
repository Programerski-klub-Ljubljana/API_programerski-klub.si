# to get a string like this run:
# openssl rand -hex 32
from datetime import datetime, timedelta
from http.client import HTTPException
from typing import Union, List

import jwt
from fastapi import Security, Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from starlette import status

from src import env

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
	"johndoe": {
		"username": "johndoe",
		"full_name": "John Doe",
		"email": "johndoe@example.com",
		"hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
		"disabled": False
	},
	"alice": {
		"username": "alice",
		"full_name": "Alice Chains",
		"email": "alicechains@example.com",
		"hashed_password": "$2b$12$gSvqqUPvlXP2tfVFaWK1Be7DlH.PKZbv5H8KnzzVgXXbVxpva.pFm",
		"disabled": True
	},
}


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	username: Union[str, None] = None
	scopes: List[str] = []


class User(BaseModel):
	username: str
	email: Union[str, None] = None
	full_name: Union[str, None] = None
	disabled: Union[bool, None] = None


class UserInDB(User):
	hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="user/login",
	scopes={"me": "Read information about the current user.", "items": "Read items."},
)


def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
	return pwd_context.hash(password)


def get_user(db, username: str):
	if username in db:
		user_dict = db[username]
		return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
	user = get_user(fake_db, username)
	if not user:
		return False
	if not verify_password(password, user.hashed_password):
		return False
	return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, env.SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


async def get_current_user(
		security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
	if security_scopes.scopes:
		authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
	else:
		authenticate_value = f"Bearer"
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": authenticate_value},
	)
	try:
		payload = jwt.decode(token, env.SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception
		token_scopes = payload.get("scopes", [])
		token_data = TokenData(scopes=token_scopes, username=username)
	except (JWTError, ValidationError):
		raise credentials_exception
	user = get_user(fake_users_db, username=token_data.username)
	if user is None:
		raise credentials_exception
	for scope in security_scopes.scopes:
		if scope not in token_data.scopes:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Not enough permissions",
				headers={"WWW-Authenticate": authenticate_value},
			)
	return user


async def get_current_active_user(current_user: User = Security(get_current_user, scopes=[])):
	if current_user.disabled:
		raise HTTPException(status_code=400, detail="Inactive user")
	return current_user
