import unittest

from core.cutils import fake
from core.domain.bancni_racun import Bancni_racun, TipTransakcije, KategorijaTransakcije, Transakcija


class test_bancni_racun(unittest.TestCase):
	def init_transakcija(self, prihodek=True, znesek: float = 0, placano: float = 0):
		return Transakcija(
			tip=TipTransakcije.PRIHODEK if prihodek else TipTransakcije.ODHODEK,
			kategorija=KategorijaTransakcije.random(),
			rok=fake.date_this_month(after_today=True),
			opis=fake.sentence(9),
			znesek=znesek,
			placano=placano)

	def test_stanje(self):
		bancni_racun = Bancni_racun(
			ime='racun', stevilka='000', transakcije=[
				self.init_transakcija(prihodek=True, znesek=10, placano=0),
				self.init_transakcija(prihodek=True, znesek=10, placano=5),
				self.init_transakcija(prihodek=True, znesek=10, placano=10),
				self.init_transakcija(prihodek=False, znesek=5, placano=0),
				self.init_transakcija(prihodek=False, znesek=5, placano=2.5),
				self.init_transakcija(prihodek=False, znesek=5, placano=5),
			])

		self.assertEqual(bancni_racun.stanje, 0 + 5 + 10 - 2.5 - 5)

	def test_dolgovi(self):
		br = Bancni_racun(
			ime='racun', stevilka='000', transakcije=[
				self.init_transakcija(prihodek=True, znesek=10, placano=0),
				self.init_transakcija(prihodek=True, znesek=10, placano=5),
				self.init_transakcija(prihodek=True, znesek=10, placano=10),
				self.init_transakcija(prihodek=False, znesek=5, placano=0),
				self.init_transakcija(prihodek=False, znesek=5, placano=2.5),
				self.init_transakcija(prihodek=False, znesek=5, placano=5),
			])

		self.assertCountEqual(br.transakcije[3:5], br.dolgovi(tip_transakcije=TipTransakcije.ODHODEK))
		self.assertEqual(br.transakcije[:2], br.dolgovi(tip_transakcije=TipTransakcije.PRIHODEK))


if __name__ == '__main__':
	unittest.main()
