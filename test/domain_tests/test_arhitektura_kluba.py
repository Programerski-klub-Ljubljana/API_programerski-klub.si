import unittest
from datetime import datetime, timedelta

from app.db import db_entities
from core.domain.arhitektura_kluba import Dovoljenja


class test_arhitektura_kluba(unittest.TestCase):

	def test_scopes(self):
		vals = Dovoljenja.values()
		scopes = Dovoljenja.scopes()
		self.assertGreater(len(vals), 0)
		self.assertEqual(len(scopes.values()), len(scopes.keys()))
		for sk, sv in scopes.items():
			self.assertIn(sk, sv)

	def test_clan_starost(self):
		clan = db_entities.init_clan(rojstro_delta_days=12 * 365 + 6 * 31)
		self.assertLess(clan.starost - 12.5, 0.01)

	def test_clan_mladoletnik(self):
		clan1 = db_entities.init_clan(rojstro_delta_days=18 * 365 + 1 * 30)
		clan2 = db_entities.init_clan(rojstro_delta_days=18 * 365 - 1 * 30)
		self.assertFalse(clan1.mladoletnik)
		self.assertTrue(clan2.mladoletnik)

	def test_clan_vpisan(self):
		clan = db_entities.init_clan()
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
		clan = db_entities.init_clan(ime='kožušček', priimek='šđžćč-ŠĐŽČĆ')
		self.assertEqual(clan.username, 'kozusceksdzcc-sdzcc')


if __name__ == '__main__':
	unittest.main()
