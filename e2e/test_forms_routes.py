import unittest
from datetime import datetime, timedelta

from starlette.testclient import TestClient

from api import API


class test_forms(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		API.init()
		cls.client = TestClient(API.fapi)

	def test_vpis(self):
		res = self.client.post('/forms/vpis', data={
			'ime': "Janez",
			'priimek': "Novak",
			'dan_rojstva': 24,
			'mesec_rojstva': 5,
			'leto_rojstva': 1992,
			'email': "jar.fmf@gmail.com",
			'telefon': "+386 051 240 885",
			'ime_skrbnika': "",
			'priimek_skrbnika': "",
			'email_skrbnika': "",
			'telefon_skrbnika': "",
		})
		self.assertTrue(res.ok)
		self.assertIn("Tvoje sporočilo je bilo sprejeto!", res.text)

	def test_vpis_mladoletnik(self):
		birth = datetime.utcnow() - timedelta(days=365 * 12)
		res = self.client.post('/forms/vpis', data={
			'ime': "Janez",
			'priimek': "Novak",
			'dan_rojstva': birth.day,
			'mesec_rojstva': birth.month,
			'leto_rojstva': birth.year,
			'email': "jar.fmf@gmail.com",
			'telefon': "+386 051 240 885",
			'ime_skrbnika': 'Micka',
			'priimek_skrbnika': 'Novak',
			'email_skrbnika': 'jar.fmf@gmail.com',
			'telefon_skrbnika': '051240885'})
		self.assertTrue(res.ok)
		self.assertIn("Tvoje sporočilo je bilo sprejeto!", res.text)


if __name__ == '__main__':
	unittest.main()
