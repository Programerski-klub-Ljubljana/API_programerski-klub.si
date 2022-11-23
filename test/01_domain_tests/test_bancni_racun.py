import unittest

from app.db import db_entities
from core.domain.bancni_racun import Bancni_racun, TipTransakcije


class test_bancni_racun(unittest.TestCase):

	def test_stanje(self):
		bancni_racun = Bancni_racun(
			ime='racun', stevilka='000', transakcije=[
				db_entities.init_transakcija(prihodek=True, znesek=10, placano=0),
				db_entities.init_transakcija(prihodek=True, znesek=10, placano=5),
				db_entities.init_transakcija(prihodek=True, znesek=10, placano=10),
				db_entities.init_transakcija(prihodek=False, znesek=5, placano=0),
				db_entities.init_transakcija(prihodek=False, znesek=5, placano=2.5),
				db_entities.init_transakcija(prihodek=False, znesek=5, placano=5),
			])

		self.assertEqual(bancni_racun.stanje, 0 + 5 + 10 - 2.5 - 5)

	def test_dolgovi(self):
		br = Bancni_racun(
			ime='racun', stevilka='000', transakcije=[
				db_entities.init_transakcija(prihodek=True, znesek=10, placano=0),
				db_entities.init_transakcija(prihodek=True, znesek=10, placano=5),
				db_entities.init_transakcija(prihodek=True, znesek=10, placano=10),
				db_entities.init_transakcija(prihodek=False, znesek=5, placano=0),
				db_entities.init_transakcija(prihodek=False, znesek=5, placano=2.5),
				db_entities.init_transakcija(prihodek=False, znesek=5, placano=5),
			])

		self.assertListEqual(br.transakcije[3:5], br.dolgovi(tip_transakcije=TipTransakcije.ODHODEK))
		self.assertEqual(br.transakcije[:2], br.dolgovi(tip_transakcije=TipTransakcije.PRIHODEK))


if __name__ == '__main__':
	unittest.main()
