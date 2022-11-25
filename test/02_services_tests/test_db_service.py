import unittest
from random import randint

from persistent.list import PersistentList

from app import APP
from core.domain._entity import Elist
from core.domain.arhitektura_kluba import Oseba, TipOsebe, Kontakt, TipKontakta, TipValidacije


class test_db(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)

		# FILL DATABASE...
		with APP.db.transaction() as root:
			for i in range(10):
				oseba = Oseba(ime=f'ime{i}', priimek=f'priimek{i}', rojen=None, kontakti=[
					Kontakt(data=f'data{i}', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)])

				root.save(oseba)

	def test_transaction_root_properties(self):
		with APP.db.transaction() as root:
			self.assertGreater(len(root.oseba), 0)
			self.assertIsInstance(root.oseba, Elist)

	def test_transaction_root_change(self):
		new_ime = '12345'

		with APP.db.transaction() as root:
			index = randint(0, len(root.oseba) - 1)
			self.assertNotEqual(root.oseba[index].ime, new_ime)
			old_ime = root.oseba[index].ime
			root.oseba[index].ime = new_ime

		with APP.db.transaction() as root:
			self.assertEqual(root.oseba[index].ime, new_ime)
			root.oseba[index].ime = old_ime

	def test_transaction_root_save(self):

		with APP.db.transaction() as root:
			# CREATE KONTACTS
			clan1 = Oseba(ime='ime1', priimek='priimek', tip_osebe=[TipOsebe.CLAN], rojen=None, kontakti=[
				Kontakt(data="a983joirow34je", tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)
			])
			clan2 = Oseba(ime='ime1', priimek='priimek', tip_osebe=[TipOsebe.CLAN], rojen=None, kontakti=[
				Kontakt(data="0392pep2opo", tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)
			])

			# ARE THEY EQUAL?
			self.assertNotEqual(clan2, clan1)

			# TEST IF LIST ARE NOT YET CONVERTED TO PERSISTENT LISTS
			self.assertIsInstance(clan1.vpisi, PersistentList)
			self.assertIsInstance(clan2.vpisi, PersistentList)

			# TEST IF KONTACTS NOT EXISTS IN DB
			assert clan1 not in root.oseba
			assert clan2 not in root.oseba

			# INSERT NEW CONTACTS
			root.save(clan1, clan2)

		# FIND CONTACTS
		clan_find1 = None
		clan_find2 = None
		with APP.db.transaction() as root:
			for clan in root.oseba:
				if clan == clan1:
					clan_find1 = clan
				if clan == clan2:
					clan_find2 = clan

			# TEST IF FOUND EQUAL TO INSERTED
			self.assertEqual(clan_find1, clan1)
			self.assertEqual(clan_find2, clan2)

			# TEST IF LIST ARE CONVERTE TO PERSISTENT LISTS
			self.assertIsInstance(clan_find1.vpisi, PersistentList)
			self.assertIsInstance(clan_find2.vpisi, PersistentList)

			# TEST IF LIST ARE CONVERTE TO PERSISTENT LISTS
			self.assertIsInstance(clan1.vpisi, PersistentList)
			self.assertIsInstance(clan2.vpisi, PersistentList)

	def test_transaction_oseba_find(self):
		with APP.db.transaction() as root:
			oseba = root.oseba[5]
			data = oseba.kontakti[-1].data
			self.assertGreater(len(data), 3)
			self.assertEqual(oseba, root.oseba_find(data))


if __name__ == '__main__':
	unittest.main()
