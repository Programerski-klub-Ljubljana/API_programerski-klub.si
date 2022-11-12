from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from app import env
from core.services.auth_service import AuthService


class Token(BaseModel):
	access_token: str
	token_type: str


class JwtAuth(AuthService):
	def __init__(self):
		self.algo = "HS256"
		self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

	def encode(self, data: dict, expiration: timedelta):
		to_encode = data.copy()  # Because you don't want to change dict instance
		expire = datetime.utcnow() + expiration
		to_encode.update({"exp": expire})
		encoded_jwt = jwt.encode(to_encode, env.SECRET_KEY, algorithm=self.algo)
		return encoded_jwt

	def decode(self, token: str):
		try:
			return jwt.decode(token, env.SECRET_KEY, algorithms=[self.algo])
		except (JWTError, ValidationError):
			return None

	def verify(self, password, hashed_password) -> bool:
		return self.pwd_context.verify(password, hashed_password)

	def hash(self, password):
		return self.pwd_context.hash(password)
