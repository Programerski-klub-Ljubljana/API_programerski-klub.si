from datetime import datetime, timedelta

from autologging import traced
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app import ENV
from core.services.auth_service import AuthService, Token


@traced
class JwtAuth(AuthService):
	def __init__(self):
		if hasattr(self, 'pwd_context'):
			raise Exception("Double init!")
		self.algo = "HS256"
		self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

	def encode(self, data: dict, expiration: timedelta) -> Token:
		to_encode = data.copy()  # Because you don't want to change dict instance
		expire = datetime.utcnow() + expiration
		to_encode.update({"exp": expire})
		encoded_jwt = jwt.encode(to_encode, ENV.SECRET_KEY, algorithm=self.algo)
		return Token(type='bearer', data=encoded_jwt)

	def decode(self, token: str):
		try:
			return jwt.decode(token, ENV.SECRET_KEY, algorithms=[self.algo])
		except (JWTError, ValidationError):
			return None

	def verify(self, password, hashed_password) -> bool:
		return self.pwd_context.verify(secret=password, hash=hashed_password)

	def hash(self, password):
		return self.pwd_context.hash(password)
