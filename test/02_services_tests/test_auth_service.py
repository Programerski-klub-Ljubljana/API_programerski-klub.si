import unittest
from datetime import timedelta

from app import APP
from app.db import db_entities
from core.services.auth_service import AuthService, TokenData


class test_auth(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service: AuthService = APP.services.auth()
		cls.data = TokenData(username='urosjarc')

	def test_encode_decode_pass(self):
		jwt = self.service.encode(data=self.data, expiration=timedelta(seconds=1))
		data_new = self.service.decode(jwt.data)

		for k, v in self.data.__dict__.items():
			self.assertEqual(self.data.__dict__[k], data_new.__dict__[k], k)

	def test_encode_decode_expirated(self):
		jwt = self.service.encode(data=self.data, expiration=timedelta(seconds=-1))
		data_new = self.service.decode(jwt.data)
		self.assertEqual(data_new, None)

	def test_decode_wrong_token(self):
		data_new = self.service.decode('asdfasdfasdfasdf')
		self.assertEqual(data_new, None)

	def test_hash_verify_pass(self):
		token = self.service.hash(db_entities.geslo)
		self.assertTrue(self.service.verify(db_entities.geslo, token))

	def test_hash_verify_fail_0(self):
		password = '1234567890'
		token = self.service.hash(password)[:-1] + 'a'
		self.assertFalse(self.service.verify(password, token))

	def test_hash_verify_fail_1(self):
		password = '1234567890'
		token = self.service.hash(password)
		self.assertFalse(self.service.verify(password[:-1] + 'a', token))

class test_token_data(unittest.TestCase):

	def test_from_token(self):
		td = TokenData(username='username')
		td.exp = '123'
		td2 = TokenData.from_token(**{'u': 'username', 'exp': '123'})
		self.assertDictEqual(td.__dict__, td2.__dict__)



if __name__ == '__main__':
	unittest.main()
