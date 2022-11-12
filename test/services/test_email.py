import unittest

from app import app
from core.services.utils import Validation


class test_email(unittest.TestCase):

	def setUp(self) -> None:
		app.init()
		self.service = app.adapters.email()

	def test_obstaja_0(self):
		email = 'jar.fmf@gmail.com'
		validation = self.service.obstaja(email)
		self.assertIsInstance(validation, Validation)
		self.assertTrue(validation.ok)
		self.assertEqual(validation.data, email)

	def test_obstaja_1(self):
		email = 'krneki'
		validation = self.service.obstaja(email)
		self.assertIsInstance(validation, Validation)
		self.assertFalse(validation.ok)
		self.assertEqual(validation.data, email)


if __name__ == '__main__':
	unittest.main()
