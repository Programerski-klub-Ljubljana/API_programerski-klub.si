import copy
import unittest
from datetime import datetime, timedelta, date

from core.domain.arhitektura_kluba import TipOsebe, Kontakt, TipKontakta, NivoValidiranosti, Oseba


class test_tip_osebe(unittest.TestCase):

	def test_dovoljenja(self):
		values = TipOsebe.values()
		dovoljenja = TipOsebe.dovoljenja()
		self.assertGreater(len(values), 0)
		self.assertEqual(len(dovoljenja.values()), len(dovoljenja.keys()))
		for sk, sv in dovoljenja.items():
			self.assertIn(sk, sv)


class test_kontakt(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		assert len(TipKontakta.values()) == 2
		assert len(NivoValidiranosti.values()) == 3

	def test_equal(self):
		k0 = Kontakt(data='1234', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)
		kontakti = [
			Kontakt(data='1234', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
		]
		fail_kontakti = [
			Kontakt(data='12343', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='12343', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='12343', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='12343', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN)
		]
		for k in kontakti:
			self.assertTrue(k0.equal(k))
			self.assertNotEqual(k0, k)
		for k in fail_kontakti:
			self.assertFalse(k0.equal(k))
			self.assertNotEqual(k0, k)


class test_oseba(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		assert len(TipKontakta.values()) == 2
		assert len(NivoValidiranosti.values()) == 3

	def test_equal_ime_priimek_rojstvo(self):
		k0 = Kontakt(data='12343', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN)
		k1 = Kontakt(data='xxxxx', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN)
		kwargs = {'tip_osebe': TipOsebe.CLAN}

		o0 = Oseba(ime='Janez', priimek='Novak', rojen=date(year=1992, month=5, day=24), kontakti=[k0], **kwargs)
		o1 = Oseba(ime='Katja', priimek='Novak', rojen=date(year=1992, month=5, day=24), kontakti=[k1], **kwargs)
		o2 = Oseba(ime='Janez', priimek='Merc', rojen=date(year=1992, month=5, day=24), kontakti=[k1], **kwargs)
		o3 = Oseba(ime='Janez', priimek='Novak', rojen=date(year=1000, month=5, day=24), kontakti=[k1], **kwargs)
		o4 = Oseba(ime='Janez', priimek='Novak', rojen=date(year=1992, month=5, day=24), kontakti=[k1], **kwargs)

		self.assertFalse(o0.equal(o1))
		self.assertFalse(o0.equal(o2))
		self.assertFalse(o0.equal(o3))
		self.assertTrue(o0.equal(o4))

	def test_equal_ime_priimek_kontakti(self):
		k = Kontakt(data='123', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)
		k0 = Kontakt(data='123', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)

		k1 = Kontakt(data='123', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN)
		k2 = Kontakt(data='123', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)
		k3 = Kontakt(data='xxx', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)
		k4 = Kontakt(data='123', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN)
		k5 = Kontakt(data='123', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)

		kwargs = {'ime': 'Janez', 'priimek': 'Novak', 'tip_osebe': [], 'rojen': None}
		o = Oseba(kontakti=[k], **kwargs)
		o0 = Oseba(kontakti=[k0], **kwargs)
		o1 = Oseba(kontakti=[k1], **kwargs)
		o2 = Oseba(kontakti=[k2], **kwargs)
		o3 = Oseba(kontakti=[k3], **kwargs)
		o4 = Oseba(kontakti=[k4], **kwargs)
		o5 = Oseba(kontakti=[k5], **kwargs)

		self.assertFalse(o0.equal(o1))
		self.assertFalse(o0.equal(o2))
		self.assertFalse(o0.equal(o3))
		self.assertFalse(o0.equal(o4))
		self.assertTrue(o0.equal(o5))

		self.assertTrue(o.equal(o1))
		self.assertTrue(o.equal(o2))
		self.assertFalse(o.equal(o3))
		self.assertFalse(o.equal(o4))
		self.assertTrue(o.equal(o5))

	def test_ima_kontakt(self):
		kwargs = {'ime': 'Janez', 'priimek': 'Novak', 'tip_osebe': [], 'rojen': None}
		o0 = Oseba(kontakti=[
			Kontakt(data='0000', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='0000', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='1111', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='2222', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
		], **kwargs)

		self.assertFalse(o0.ima_kontakt('0000'))
		self.assertTrue(o0.ima_kontakt('2222'))

	def test_dodaj_kontakte(self):
		k0 = Kontakt(data='0000', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)
		k1 = Kontakt(data='0000', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN)
		k2 = Kontakt(data='1111', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN)

		kwargs = {'ime': 'Janez', 'priimek': 'Novak', 'tip_osebe': [], 'rojen': None}
		o0 = Oseba(kontakti=[
			Kontakt(data='0000', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='0000', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='0000', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
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
			Kontakt(data='xxx', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
		], **kwargs)

		self.assertEqual(str(o0),
		                 "Oseba(ime='Janez', priimek='Novak', rojen=datetime.date(1992, 5, 24), geslo=None, tip_osebe=[], kontakti=[], vpisi=[], izpisi=[])")
		self.assertEqual(str(o1),
		                 "Oseba(ime='Janez', "
		                 "priimek='Novak', "
		                 "rojen=None, "
		                 "geslo=None, "
		                 "tip_osebe=[], "
		                 "kontakti=["
		                 "Kontakt(data='123', tip=<TipKontakta.EMAIL: 'EMAIL'>, nivo_validiranosti=<NivoValidiranosti.NI_VALIDIRAN: 'NI_VALIDIRAN'>), "
		                 "Kontakt(data='xxx', tip=<TipKontakta.EMAIL: 'EMAIL'>, nivo_validiranosti=<NivoValidiranosti.POTRJEN: 'POTRJEN'>)], "
		                 "vpisi=[], "
		                 "izpisi=[])")

	def test_nov_vpis_in_vpis(self):
		o = Oseba(ime='Janez', priimek='Novak', tip_osebe=[], rojen=None)
		t = datetime.now()

		self.assertEqual(len(o.vpisi), 0)
		self.assertEqual(len(o.izpisi), 0)

		o.nov_izpis()
		self.assertEqual(len(o.vpisi), 0)
		self.assertEqual(len(o.izpisi), 0)

		o.nov_vpis()
		self.assertEqual(len(o.vpisi), 1)
		self.assertEqual(len(o.izpisi), 0)
		self.assertGreater(o.vpisi[-1], t)

		o.nov_vpis()
		self.assertEqual(len(o.vpisi), 1)
		self.assertEqual(len(o.izpisi), 0)
		self.assertGreater(o.vpisi[-1], t)

		o.nov_izpis()
		self.assertEqual(len(o.vpisi), 1)
		self.assertEqual(len(o.izpisi), 1)
		self.assertGreater(o.vpisi[-1], t)
		self.assertGreater(o.izpisi[-1], t)

		o.nov_izpis()
		self.assertEqual(len(o.vpisi), 1)
		self.assertEqual(len(o.izpisi), 1)
		self.assertGreater(o.vpisi[-1], t)
		self.assertGreater(o.izpisi[-1], t)

		o.nov_vpis()
		self.assertEqual(len(o.vpisi), 2)
		self.assertEqual(len(o.izpisi), 1)
		self.assertGreater(o.vpisi[-1], t)
		self.assertGreater(o.izpisi[-1], t)

	def test_starost(self):
		o = Oseba(ime='Janez', priimek='Novak', tip_osebe=[], rojen=datetime.now() - timedelta(days=12 * 365 + 6 * 31 + 10))
		self.assertEqual(round(o.starost, 1), 12.5)

	def test_mladoletnik(self):
		o0 = Oseba(ime='Janez', priimek='Novak', tip_osebe=[], rojen=datetime.now() - timedelta(days=18 * 365 + 30))
		o1 = Oseba(ime='Janez', priimek='Novak', tip_osebe=[], rojen=datetime.now() - timedelta(days=18 * 365 - 30))
		self.assertFalse(o0.mladoletnik)
		self.assertTrue(o1.mladoletnik)

	def test_vpisan(self):
		o2 = Oseba(ime='Janez', priimek='Novak', rojen=None, tip_osebe=TipOsebe.CLAN)
		self.assertFalse(o2.vpisan)
		o2.vpisi.append(datetime.now() + timedelta(days=5))
		self.assertTrue(o2.vpisan)

		o2.vpisi.append(datetime.now() + timedelta(days=5))
		o2.izpisi.append(datetime.now() + timedelta(days=10))
		self.assertFalse(o2.vpisan)

		o2.vpisi.append(datetime.now() + timedelta(days=10))
		o2.izpisi.append(datetime.now() + timedelta(days=5))
		self.assertTrue(o2.vpisan)

	def test_merge_vpisi_izpisi(self):
		vpisi = [datetime.now() - timedelta(days=i * 10) for i in range(4)]
		izpisi = [datetime.now() - timedelta(days=i * 5) for i in range(4)]

		empty_oseba0 = Oseba(ime='ime', priimek='priimek', rojen=date.today(), geslo=None, tip_osebe=[], kontakti=[], vpisi=[], izpisi=[])
		empty_oseba1 = copy.deepcopy(empty_oseba0)
		empty_oseba2 = copy.deepcopy(empty_oseba0)
		empty_oseba3 = copy.deepcopy(empty_oseba0)
		empty_oseba3.ime = 'xxx'

		full_oseba0 = Oseba(ime='ime', priimek='priimek', rojen=date.today(), geslo='geslo', tip_osebe=[TipOsebe.CLAN, TipOsebe.SKRBNIK], kontakti=[
			Kontakt(data='data0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='data1', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='data2', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='data3', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='data4', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='data5', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN),
		], vpisi=vpisi, izpisi=izpisi)
		full_oseba1 = copy.deepcopy(full_oseba0)

		# HALF OSEBA (TEST IF ROJEN IS NONE AND HAVE KONTAKTS CONFIRMED
		half_oseba = copy.deepcopy(full_oseba0)
		half_oseba.rojen = None
		half_oseba.tip_osebe = half_oseba.tip_osebe[:1]
		half_oseba.kontakti = half_oseba.kontakti[:1]
		half_oseba.vpisi = half_oseba.vpisi[:2]
		half_oseba.izpisi = half_oseba.izpisi[:2]

		# MERGE RETURN FALSE ON OSEBA NOT MATCHING!
		self.assertFalse(empty_oseba3.merge(full_oseba0, merge_kontakti=True, merge_vpisi_izpisi=True))
		self.assertFalse(full_oseba0.merge(empty_oseba3, merge_kontakti=True, merge_vpisi_izpisi=True))

		# AFTER FAILED MERGE NOTHING SHOULD CHANGE!
		self.assertEqual(full_oseba0, full_oseba1)

		# TEST IF OBJECTS ARE STILL REALLY EQUAL
		self.assertEqual(full_oseba0, full_oseba1)
		self.assertEqual(empty_oseba0, empty_oseba1)
		self.assertEqual(empty_oseba0, empty_oseba2)
		self.assertNotEqual(empty_oseba0, empty_oseba3)
		self.assertNotEqual(half_oseba, full_oseba0)

		self.assertTrue(full_oseba0.merge(full_oseba0, merge_vpisi_izpisi=True, merge_kontakti=True))
		self.assertTrue(empty_oseba0.merge(empty_oseba1, merge_vpisi_izpisi=True, merge_kontakti=True))
		self.assertTrue(empty_oseba2.merge(empty_oseba1, merge_vpisi_izpisi=False, merge_kontakti=True))

		# MERGE SAME OBJECT SHOULD NOT CHANGE ANYTHING
		self.assertEqual(full_oseba0, full_oseba1)
		self.assertEqual(empty_oseba0, empty_oseba1)
		self.assertEqual(empty_oseba0, empty_oseba2)

		self.assertTrue(empty_oseba0.merge(full_oseba0, merge_vpisi_izpisi=True, merge_kontakti=True))
		self.assertTrue(half_oseba.merge(full_oseba0, merge_vpisi_izpisi=True, merge_kontakti=True))
		self.assertTrue(full_oseba1.merge(empty_oseba1, merge_vpisi_izpisi=True, merge_kontakti=True))

		# MERGE ORDER SHOULD NOT BE IMPORTANT!
		self.assertEqual(empty_oseba0, full_oseba0)
		self.assertEqual(full_oseba0, full_oseba1)
		self.assertEqual(half_oseba, full_oseba1)

		self.assertTrue(empty_oseba2.merge(full_oseba0, merge_vpisi_izpisi=False, merge_kontakti=True))
		self.assertEqual(empty_oseba2.ime, full_oseba0.ime)
		self.assertEqual(empty_oseba2.priimek, full_oseba0.priimek)
		self.assertEqual(empty_oseba2.rojen, full_oseba0.rojen)
		self.assertEqual(empty_oseba2.geslo, full_oseba0.geslo)
		self.assertEqual(empty_oseba2.tip_osebe, full_oseba0.tip_osebe)
		self.assertEqual(empty_oseba2.kontakti, full_oseba0.kontakti)
		self.assertEqual(empty_oseba2.vpisi, [])
		self.assertEqual(empty_oseba2.izpisi, [])


if __name__ == '__main__':
	unittest.main()
