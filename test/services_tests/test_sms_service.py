import unittest

from app import APP


class test_sms(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service = APP.services.sms()

	def test_obstaja_0(self):
		phone = '+386051240885'
		self.assertTrue(
			self.service.obstaja(phone)
		)

	def test_obstaja_1(self):
		phone = 'krneki'
		self.assertFalse(
			self.service.obstaja(phone)
		)

	def test_obstaja_2(self):
		phone = '+386 051 240 885'
		self.assertTrue(
			self.service.obstaja(phone)
		)

	def test_obstaja_3(self):
		phone = '+386/051/240/885'
		self.assertFalse(
			self.service.obstaja(phone)
		)

	def test_obstaja_4(self):
		phone = '+386-051-240-885'
		self.assertTrue(
			self.service.obstaja(phone)
		)

	def test_obstaja_5(self):
		phone = '051240885'
		self.assertFalse(
			self.service.obstaja(phone)
		)


if __name__ == '__main__':
	unittest.main()
