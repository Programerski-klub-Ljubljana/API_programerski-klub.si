from datetime import datetime, timedelta

from autologging import traced
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from core.services.auth_service import AuthService, Token, TokenData


@traced
class JwtAuth(AuthService):
	def __init__(self, secret: str):
		if hasattr(self, 'pwd_context'):
			raise Exception("Double init!")
		self.algo = "HS256"
		self.secret = secret
		self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

	def encode(self, data: TokenData, expiration: timedelta) -> Token:
		data.exp = datetime.utcnow() + expiration
		encoded_jwt = jwt.encode(data.__dict__, self.secret, algorithm=self.algo)
		return Token(type='bearer', data=encoded_jwt)

	def decode(self, token: str) -> TokenData:
		try:
			return TokenData(**jwt.decode(token, self.secret, algorithms=[self.algo]))
		except (JWTError, ValidationError):
			return None

	def verify(self, password, hashed_password) -> bool:
		return self.pwd_context.verify(secret=password, hash=hashed_password)

	def hash(self, password):
		return self.pwd_context.hash(password)
