import unittest
from datetime import datetime, timedelta

from starlette.testclient import TestClient

from api import API
from app import APP, CONST
from app.db.db_entities import fake
from core.services.email_service import EmailService


class test_forms(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		API.init()
		cls.email: EmailService = APP.services.email()
		cls.client = TestClient(API.fapi)
		cls.testing_email = 'jar.fmf@gmail.com'
		cls.testing_email_skrbnik = 'jarf.mf@gmail.com'
		cls.testing_phone = '051240885'

	def vpis_data(self, mladoletnik: bool = False, **kwargs):
		starost = 12 if mladoletnik else 25
		rojstvo = datetime.utcnow() - timedelta(days=365 * starost)
		data = {
			'ime': fake.first_name(),
			'priimek': fake.last_name(),
			'dan_rojstva': rojstvo.day,
			'mesec_rojstva': rojstvo.month,
			'leto_rojstva': rojstvo.year,
			'email': self.testing_email,
			'telefon': self.testing_phone}

		skrbnik = {
			'ime_skrbnika': fake.first_name(),
			'priimek_skrbnika': fake.last_name(),
			'email_skrbnika': self.testing_email_skrbnik,
			'telefon_skrbnika': self.testing_phone}

		if mladoletnik: data = {**data, **skrbnik}
		return {**data, **kwargs}

	def test_vpis(self):
		with self.email.record() as history:
			res = self.client.post('/forms/vpis', data=self.vpis_data(mladoletnik=False))
			self.assertTrue(res.ok)
			self.assertIn("Tvoje sporočilo je bilo sprejeto!", res.text)
			self.assertEqual(len(history), 1)
			self.assertEqual(history[0]['To'], self.testing_email)
			self.assertEqual(CONST.subject.vpis, history[0]['Subject'])

	def test_vpis_mladoletnik(self):
		with self.email.record() as history:
			res = self.client.post('/forms/vpis', data=self.vpis_data(mladoletnik=True))
			self.assertTrue(res.ok)
			self.assertIn("Tvoje sporočilo je bilo sprejeto!", res.text)
			self.assertEqual(len(history), 2)
			self.assertEqual(history[0]['To'], self.testing_email)
			self.assertEqual(history[1]['To'], self.testing_email_skrbnik)
			self.assertEqual(CONST.subject.vpis, history[0]['Subject'])
			self.assertEqual(CONST.subject.vpis_skrbnik, history[1]['Subject'])


if __name__ == '__main__':
	unittest.main()
