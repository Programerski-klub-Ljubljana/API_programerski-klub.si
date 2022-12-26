import unittest
from datetime import datetime

from app import APP, CONST
from core.services.phone_service import PhoneService, PhoneOrigin


class test_phone(unittest.TestCase):
	phone_codes = {
		'+39': {'languages': ['it'], 'country': 'IT', 'name': 'Italia'},
		'+43': {'languages': ['de'], 'country': 'AT', 'name': 'Österreich'},
		'+36': {'languages': ['hu'], 'country': 'HU', 'name': 'Magyarország'},
		'+385': {'languages': ['hr'], 'country': 'HR', 'name': 'Hrvatska'},
		'+386': {'languages': ['sl'], 'country': 'SI', 'name': 'Slovenija'}
	}

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.api_phone = CONST.phones.api
		cls.testing_phone = CONST.phones.test
		cls.service: PhoneService = APP.services.phone()

	def test_check_existance(self):
		self.assertTrue(self.service.check_existance(self.api_phone))

	def test_send_sms(self):
		text = f"TESTING: {datetime.now()}"
		self.assertTrue(self.service.send_sms(self.api_phone, text))

	def test_format(self):
		correct_form = "+38651234567"
		phone = '051234567'
		self.assertEqual(self.service.format(f'+386{phone}'), correct_form)
		self.assertEqual(self.service.format(phone), correct_form)
		self.assertEqual(self.service.format('krneki'), 'krneki')
		self.assertEqual(self.service.format('+386/051-234 567'), correct_form)

	def test_origin(self):
		expected = PhoneOrigin(languages=['sl'], country="SI", name="Slovenija")
		empty = PhoneOrigin(languages=[], country=None, name=None)

		phone = '051234567'
		self.assertEqual(self.service.origin(f'+386{phone}'), expected)
		self.assertEqual(self.service.origin(phone), expected)
		self.assertEqual(self.service.origin('krneki'), empty)
		self.assertEqual(self.service.origin('+386/051-234 567'), expected)

		for code, country_info in self.phone_codes.items():
			self.assertEqual(self.service.origin(f'{code}{phone}'), PhoneOrigin(**country_info))




if __name__ == '__main__':
	unittest.main()
