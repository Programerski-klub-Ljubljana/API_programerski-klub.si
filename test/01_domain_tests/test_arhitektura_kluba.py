import unittest
from datetime import datetime, timedelta

from app.db import db_entities
from core.domain.arhitektura_kluba import TipOsebe, Kontakt, TipKontakta, TipValidacije


class test_tip_osebe(unittest.TestCase):

	def test_scopes(self):
		vals = TipOsebe.values()
		scopes = TipOsebe.scopes()
		self.assertGreater(len(vals), 0)
		self.assertEqual(len(scopes.values()), len(scopes.keys()))
		for sk, sv in scopes.items():
			self.assertIn(sk, sv)


class test_kontakt(unittest.TestCase):

	def test_eq(self):
		k0 = Kontakt(data='1234', tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN)
		kontakti = [
			Kontakt(data='1234', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='1234', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN),
			Kontakt(data='1234', tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN),
			Kontakt(data='1234', tip=TipKontakta.PHONE, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='1234', tip=TipKontakta.PHONE, validacija=TipValidacije.POTRJEN)
		]
		for k in kontakti:
			self.assertEqual(k0, k)



class test_oseba(unittest.TestCase):

	def test_starost(self):
		clan = db_entities.init_oseba(rojstro_delta_days=12 * 365 + 6 * 31)
		self.assertLess(clan.starost - 12.5, 0.01)

	def test_mladoletnik(self):
		clan1 = db_entities.init_oseba(rojstro_delta_days=18 * 365 + 1 * 30)
		clan2 = db_entities.init_oseba(rojstro_delta_days=18 * 365 - 1 * 30)
		self.assertFalse(clan1.mladoletnik)
		self.assertTrue(clan2.mladoletnik)

	def test_vpisan(self):
		clan = db_entities.init_oseba(vpisi=[], izpisi=[])
		self.assertFalse(clan.vpisan)
		clan.vpisi.append(datetime.utcnow() + timedelta(days=5))
		self.assertTrue(clan.vpisan)

		clan.vpisi.append(datetime.utcnow() + timedelta(days=5))
		clan.izpisi.append(datetime.utcnow() + timedelta(days=10))
		self.assertFalse(clan.vpisan)

		clan.vpisi.append(datetime.utcnow() + timedelta(days=10))
		clan.izpisi.append(datetime.utcnow() + timedelta(days=5))
		self.assertTrue(clan.vpisan)

	def test_username(self):
		clan = db_entities.init_oseba(ime='kožušček', priimek='šđžćč-ŠĐŽČĆ')
		self.assertTrue(clan.has_username('jar.fmf@gmail.com'))
		self.assertFalse(clan.has_username('jarc.fmf@gmail.com'))


if __name__ == '__main__':
	unittest.main()
