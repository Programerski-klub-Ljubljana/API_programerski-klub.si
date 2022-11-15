import unittest
from datetime import datetime, timedelta
from random import randint

from core.domain.arhitektura_kluba import Dovoljenja, Clan
from core.domain.bancni_racun import Bancni_racun, TipTransakcije, Transakcija, KategorijaTransakcije


class test_arhitektura_kluba(unittest.TestCase):

	def clan(self, dni):
		return Clan(
			ime=None, priimek=None, rojen=datetime.utcnow() - timedelta(days=dni), geslo=None, dovoljenja=None, email=None, telefon=None,
			skrbniki=None, vpisi=None, izpisi=None)

	def test_scopes(self):
		vals = Dovoljenja.values()
		scopes = Dovoljenja.scopes()
		self.assertGreater(len(vals), 0)
		self.assertEqual(len(scopes.values()), len(scopes.keys()))
		for sk, sv in scopes.items():
			self.assertIn(sk, sv)

	def test_clan_starost(self):
		clan = self.clan(12 * 365 + 6 * 31)
		self.assertLess(clan.starost - 12.5, 0.01)

	def test_clan_mladoletnik(self):
		clan1 = self.clan(18 * 365 + 1 * 30)
		clan2 = self.clan(18 * 365 - 1 * 30)
		self.assertFalse(clan1.mladoletnik)
		self.assertTrue(clan2.mladoletnik)

	def test_clan_vpisan(self):
		clan = self.clan(0)
		clan.vpisi.append(datetime.utcnow() - timedelta(days=-1))
		clan.izpisi.append(datetime.utcnow() - timedelta(days=1))
		self.assertTrue(clan.vpisan)


class test_bancni_racun(unittest.TestCase):

	def transakcija(self, prihodek=True, znesek: float = 0, placano: float = 0):
		return Transakcija(
			tip=TipTransakcije.PRIHODEK if prihodek else TipTransakcije.ODHODEK,
			kategorija=KategorijaTransakcije.random(),
			rok=datetime.utcnow() + timedelta(days=randint(-5, 5)),
			opis='opis',
			znesek=znesek,
			placano=placano
		)

	def test_stanje(self):
		bancni_racun = Bancni_racun(
			ime='racun', stevilka='000', transakcije=[
				self.transakcija(prihodek=True, znesek=10, placano=0),
				self.transakcija(prihodek=True, znesek=10, placano=5),
				self.transakcija(prihodek=True, znesek=10, placano=10),
				self.transakcija(prihodek=False, znesek=5, placano=0),
				self.transakcija(prihodek=False, znesek=5, placano=2.5),
				self.transakcija(prihodek=False, znesek=5, placano=5),
			])

		self.assertEqual(bancni_racun.stanje, 0 + 5 + 10 - 2.5 - 5)

	def test_dolgovi(self):
		br = Bancni_racun(
			ime='racun', stevilka='000', transakcije=[
				self.transakcija(prihodek=True, znesek=10, placano=0),
				self.transakcija(prihodek=True, znesek=10, placano=5),
				self.transakcija(prihodek=True, znesek=10, placano=10),
				self.transakcija(prihodek=False, znesek=5, placano=0),
				self.transakcija(prihodek=False, znesek=5, placano=2.5),
				self.transakcija(prihodek=False, znesek=5, placano=5),
			])

		self.assertListEqual(br.transakcije[3:5], br.dolgovi(tip_transakcije=TipTransakcije.ODHODEK))
		self.assertEqual(br.transakcije[:2], br.dolgovi(tip_transakcije=TipTransakcije.PRIHODEK))


if __name__ == '__main__':
	unittest.main()
