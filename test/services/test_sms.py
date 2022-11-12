import unittest

from app import app
from core.services.utils import Validation


class test_sms(unittest.TestCase):

	def setUp(self) -> None:
		app.init()
		self.service = app.adapters.sms()

	def test_obstaja_0(self):
		phone = '+386051240885'
		validation = self.service.obstaja(phone)
		self.assertIsInstance(validation, Validation)
		self.assertTrue(validation.ok)
		self.assertEqual(validation.data, phone)

	def test_obstaja_1(self):
		phone = 'krneki'
		validation = self.service.obstaja(phone)
		self.assertIsInstance(validation, Validation)
		self.assertFalse(validation.ok)
		self.assertEqual(validation.data, phone)

	def test_obstaja_2(self):
		phone = '+386 051 240 885'
		self.assertTrue(self.service.obstaja(phone).ok)

	def test_obstaja_3(self):
		phone = '+386/051/240/885'
		self.assertFalse(self.service.obstaja(phone).ok)

	def test_obstaja_4(self):
		phone = '+386-051-240-885'
		self.assertTrue(self.service.obstaja(phone).ok)

	def test_obstaja_5(self):
		phone = '051240885'
		self.assertFalse(self.service.obstaja(phone).ok)


if __name__ == '__main__':
	unittest.main()
