import unittest
from datetime import datetime, timedelta, date

from core.domain.arhitektura_kluba import TipOsebe, Kontakt, TipKontakta, TipValidacije, Oseba


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
		fail_kontakti = [
			Kontakt(data='12343', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='12343', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN),
			Kontakt(data='12343', tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN),
			Kontakt(data='12343', tip=TipKontakta.PHONE, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='12343', tip=TipKontakta.PHONE, validacija=TipValidacije.POTRJEN)
		]
		for k in kontakti:
			self.assertEqual(k0, k)
		for k in fail_kontakti:
			self.assertNotEqual(k0, k)


class test_oseba(unittest.TestCase):

	def test_eq_ime_priimek_rojstvo(self):
		k0 = Kontakt(data='12343', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN)
		k1 = Kontakt(data='xxxxx', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN)
		kwargs = {'tip_osebe': TipOsebe.CLAN}

		o0 = Oseba(ime='Janez', priimek='Novak', rojen=date(year=1992, month=5, day=24), kontakti=[k0], **kwargs)
		o1 = Oseba(ime='Katja', priimek='Novak', rojen=date(year=1992, month=5, day=24), kontakti=[k1], **kwargs)
		o2 = Oseba(ime='Janez', priimek='Merc', rojen=date(year=1992, month=5, day=24), kontakti=[k1], **kwargs)
		o3 = Oseba(ime='Janez', priimek='Novak', rojen=date(year=1000, month=5, day=24), kontakti=[k1], **kwargs)
		o4 = Oseba(ime='Janez', priimek='Novak', rojen=date(year=1992, month=5, day=24), kontakti=[k1], **kwargs)

		self.assertNotEqual(o0, o1)
		self.assertNotEqual(o0, o2)
		self.assertNotEqual(o0, o3)
		self.assertEqual(o0, o4)

	def test_eq_ime_priimek_kontakti(self):
		k0 = Kontakt(data='123', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)
		k1 = Kontakt(data='123', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN)
		k2 = Kontakt(data='123', tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN)
		k3 = Kontakt(data='xxx', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)
		k4 = Kontakt(data='123', tip=TipKontakta.PHONE, validacija=TipValidacije.POTRJEN)
		k5 = Kontakt(data='123', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)

		kwargs = {'ime': 'Janez', 'priimek': 'Novak', 'tip_osebe': [], 'rojen': None}
		o0 = Oseba(kontakti=[k0], **kwargs)
		o1 = Oseba(kontakti=[k1], **kwargs)
		o2 = Oseba(kontakti=[k2], **kwargs)
		o3 = Oseba(kontakti=[k3], **kwargs)
		o4 = Oseba(kontakti=[k4], **kwargs)
		o5 = Oseba(kontakti=[k5], **kwargs)

		self.assertNotEqual(o0, o1)
		self.assertNotEqual(o0, o2)
		self.assertNotEqual(o0, o3)
		self.assertNotEqual(o0, o4)
		self.assertEqual(o0, o5)

	def test_has_username(self):
		kwargs = {'ime': 'Janez', 'priimek': 'Novak', 'tip_osebe': [], 'rojen': None}
		o0 = Oseba(kontakti=[
			Kontakt(data='0000', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='0000', tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
			Kontakt(data='1111', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN),
			Kontakt(data='2222', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN),
		], **kwargs)

		self.assertFalse(o0.has_kontakt_data('0000'))
		self.assertTrue(o0.has_kontakt_data('2222'))

	def test_dodaj_kontakte(self):
		k0 = Kontakt(data='0000', tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN)
		k1 = Kontakt(data='0000', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN)
		k2 = Kontakt(data='1111', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN)

		kwargs = {'ime': 'Janez', 'priimek': 'Novak', 'tip_osebe': [], 'rojen': None}
		o0 = Oseba(kontakti=[
			Kontakt(data='0000', tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
			Kontakt(data='0000', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='0000', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN),
		], **kwargs)

		self.assertEqual(len(o0.kontakti), 3)
		o0.dodaj_kontakte(k0)
		self.assertEqual(len(o0.kontakti), 3)
		o0.dodaj_kontakte(k1)
		self.assertEqual(len(o0.kontakti), 3)
		o0.dodaj_kontakte(k2)
		self.assertEqual(len(o0.kontakti), 4)
		o0.dodaj_kontakte(k0, k1)
		self.assertEqual(len(o0.kontakti), 4)

	def test_dodaj_tip_osebe(self):
		kwargs = {'ime': 'Janez', 'priimek': 'Novak', 'tip_osebe': [], 'rojen': None}
		o0 = Oseba(kontakti=[], **kwargs)

		self.assertEqual(len(o0.tip_osebe), 0)
		o0.dodaj_tip_osebe(TipOsebe.CLAN)
		self.assertEqual(len(o0.tip_osebe), 1)
		o0.dodaj_tip_osebe(TipOsebe.CLAN)
		self.assertEqual(len(o0.tip_osebe), 1)
		o0.dodaj_tip_osebe(TipOsebe.SKRBNIK)
		self.assertEqual(len(o0.tip_osebe), 2)
		o0.dodaj_tip_osebe(TipOsebe.SKRBNIK)
		self.assertEqual(len(o0.tip_osebe), 2)

	def test_str(self):
		kwargs = {'ime': 'Janez', 'priimek': 'Novak', 'tip_osebe': []}
		o0 = Oseba(rojen=date(year=1992, month=5, day=24), kontakti=[], **kwargs)

		o1 = Oseba(rojen=None, kontakti=[
			Kontakt(data='123', tip=TipKontakta.EMAIL),
			Kontakt(data='xxx', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN),
		], **kwargs)

		self.assertEqual(str(o0), "janeznovak_24051992")
		self.assertEqual(str(o1), "janeznovak_xxx")

	def test_nov_vpis(self):
		o = Oseba(ime='Janez', priimek='Novak', tip_osebe=[], rojen=None)
		t = datetime.utcnow()
		self.assertEqual(len(o.vpisi), 0)
		o.nov_vpis()
		self.assertEqual(len(o.vpisi), 1)
		o.nov_vpis()
		self.assertEqual(len(o.vpisi), 2)
		self.assertGreater(o.vpisi[-1], t)

	def test_starost(self):
		o = Oseba(ime='Janez', priimek='Novak', tip_osebe=[], rojen=datetime.utcnow() - timedelta(days=12 * 365 + 6 * 31 + 10))
		self.assertEqual(round(o.starost, 2), 12.52)

	def test_mladoletnik(self):
		o0 = Oseba(ime='Janez', priimek='Novak', tip_osebe=[], rojen=datetime.utcnow() - timedelta(days=18 * 365 + 30))
		o1 = Oseba(ime='Janez', priimek='Novak', tip_osebe=[], rojen=datetime.utcnow() - timedelta(days=18 * 365 - 30))
		self.assertFalse(o0.mladoletnik)
		self.assertTrue(o1.mladoletnik)

	def test_vpisan(self):
		o2 = Oseba(ime='Janez', priimek='Novak', rojen=None, tip_osebe=TipOsebe.CLAN)
		self.assertFalse(o2.vpisan)
		o2.vpisi.append(datetime.utcnow() + timedelta(days=5))
		self.assertTrue(o2.vpisan)

		o2.vpisi.append(datetime.utcnow() + timedelta(days=5))
		o2.izpisi.append(datetime.utcnow() + timedelta(days=10))
		self.assertFalse(o2.vpisan)

		o2.vpisi.append(datetime.utcnow() + timedelta(days=10))
		o2.izpisi.append(datetime.utcnow() + timedelta(days=5))
		self.assertTrue(o2.vpisan)


if __name__ == '__main__':
	unittest.main()
