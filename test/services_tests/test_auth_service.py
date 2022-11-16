import unittest
from datetime import timedelta

from app import APP
from core.services.auth_service import AuthService


class test_auth(unittest.TestCase):

	def setUp(self) -> None:
		APP.init(seed=False)
		self.service: AuthService = APP.services.auth()
		self.data = {'username': 'urosjarc'}

	def test_encode_decode_pass(self):
		jwt = self.service.encode(data=self.data, expiration=timedelta(seconds=1))
		data_new = self.service.decode(jwt.data)

		for k, v in self.data.items():
			self.assertEqual(self.data[k], data_new[k], k)

	def test_encode_decode_expirated(self):
		jwt = self.service.encode(data=self.data, expiration=timedelta(seconds=-1))
		data_new = self.service.decode(jwt.data)
		self.assertEqual(data_new, None)

	def test_decode_wrong_token(self):
		data_new = self.service.decode('asdfasdfasdfasdf')
		self.assertEqual(data_new, None)

	def test_hash_verify_pass(self):
		password = 'geslo'
		hash = self.service.hash(password)
		print(hash)
		self.assertTrue(self.service.verify(password, hash))

	def test_hash_verify_fail_0(self):
		password = '1234567890'
		hash = self.service.hash(password)[:-1] + 'a'
		self.assertFalse(self.service.verify(password, hash))

	def test_hash_verify_fail_1(self):
		password = '1234567890'
		hash = self.service.hash(password)
		self.assertFalse(self.service.verify(password[:-1] + 'a', hash))


if __name__ == '__main__':
	unittest.main()
