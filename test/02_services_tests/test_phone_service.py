import unittest
from datetime import datetime

from app import APP
from core.services.phone_service import PhoneService


class test_phone(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service: PhoneService = APP.services.phone()

	def test_check_existance(self):
		self.assertTrue(self.service.check_existance('051240885'))

	def test_send_sms(self):
		text = f"TESTING: {datetime.utcnow()}"
		self.assertTrue(self.service.send_sms('+38651240885', text))

	def test_format(self):
		correct_form = "+38651240885"
		self.assertEqual(self.service.format('+386051240885'), correct_form)
		self.assertEqual(self.service.format('051240885'), correct_form)
		self.assertEqual(self.service.format('krneki'), 'krneki')
		self.assertEqual(self.service.format('+386/051-240 885'), correct_form)


if __name__ == '__main__':
	unittest.main()
