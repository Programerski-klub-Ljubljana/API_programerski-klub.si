import unittest
from datetime import datetime

from persistent.list import PersistentList

from app import app
from core.domain._entity import Elist, Log
from core.domain._enums import LogTheme, LogLevel
from core.domain.arhitektura_kluba import Kontakt, TipKontakta
from core.services.db_service import DbService


class test_db(unittest.TestCase):
	service = None

	@classmethod
	def setUpClass(cls) -> None:
		app.init()

		cls.service: DbService = app.services.db()

		# TEST IF EMPTY
		count = 0
		with cls.service.transaction() as root:
			for k, v in root.__dict__.items():
				count += 1
				assert len(v) == 0 and isinstance(v, Elist)

		cls.service.seed()

	def test_transaction(self):
		count = 0
		with self.service.transaction() as root:
			for k, v in root.__dict__.items():
				count += 1
				self.assertGreater(len(v), 0, k)
				self.assertIsInstance(v, Elist)
		self.assertGreater(count, 0)

	def test_entity_properties(self):
		with self.service.transaction() as root:
			k = root.kontakt[0]
			self.assertEqual(k._razred, 'KONTAKT')
			self.assertLessEqual(k._ustvarjen, datetime.utcnow())
			self.assertLessEqual(k._posodobljen, datetime.utcnow())
			self.assertGreaterEqual(len(k._dnevnik), 0)
			self.assertGreaterEqual(len(k._povezave), 0)

	def test_transaction_change(self):
		ime = 'ime'
		with self.service.transaction() as root:
			self.assertNotEqual(root.clan[0].ime, ime)
			root.clan[0].ime = ime

		with self.service.transaction() as root:
			self.assertEqual(root.clan[0].ime, ime)

	def test_transaction_save_append(self):
		# CREATE KONTACTS
		kontakt_new = Kontakt(ime='ime', priimek='priimek', tip=TipKontakta.SKRBNIK, email=['jar.fmf@gmail.com'], telefon=['051248885'])
		kontakt_new2 = Kontakt(ime='ime2', priimek='priimek2', tip=TipKontakta.SKRBNIK, email=['jar.fmf@gmail.com'], telefon=['051248885'])

		# ARE THEY EQUAL?
		self.assertNotEqual(kontakt_new2, kontakt_new)

		# TEST IF LIST ARE NOT YET CONVERTED TO PERSISTENT LISTS
		self.assertNotIsInstance(kontakt_new.email, PersistentList)
		self.assertNotIsInstance(kontakt_new2.email, PersistentList)

		# TEST IF KONTACTS NOT EXISTS IN DB
		with self.service.transaction() as root:
			assert kontakt_new not in root.kontakt
			assert kontakt_new2 not in root.kontakt

			# INSERT NEW CONTACTS
			root.save(kontakt_new)
			root.kontakt.append(kontakt_new2)

		# FIND CONTACTS
		kontakt_find = None
		kontakt_find2 = None
		with self.service.transaction() as root:
			for kontakt in root.kontakt:
				if kontakt == kontakt_new:
					kontakt_find = kontakt
				if kontakt == kontakt_new2:
					kontakt_find2 = kontakt

		# TEST IF FOUND EQUAL TO INSERTED
		self.assertEqual(kontakt_find, kontakt_new)
		self.assertEqual(kontakt_find2, kontakt_new2)

		# TEST IF LIST ARE CONVERTE TO PERSISTENT LISTS
		self.assertIsInstance(kontakt_find.email, PersistentList)
		self.assertIsInstance(kontakt_find2.email, PersistentList)

		# TEST IF LIST ARE CONVERTE TO PERSISTENT LISTS
		self.assertIsInstance(kontakt_new.email, PersistentList)
		self.assertIsInstance(kontakt_new2.email, PersistentList)

	def test_transaction_random_0(self):
		with self.service.transaction() as root:
			kontakt = root.kontakt.random()
			kontakt2 = root.kontakt.random()
			self.assertNotEqual(kontakt, kontakt2)
			self.assertIn(kontakt, root.kontakt)
			self.assertIn(kontakt2, root.kontakt)
			self.assertNotEqual(root.kontakt.index(kontakt), root.kontakt.index(kontakt2))

	def test_transaction_random_1(self):
		with self.service.transaction() as root:
			kontakts = root.kontakt.random(k=3)
			self.assertTrue(kontakts[0] != kontakts[1] != kontakts[2])
			for k in kontakts:
				self.assertIn(k, root.kontakt)

	def test_povezi(self):
		log = Log(nivo=LogLevel.ERROR, tema=LogTheme.PROBLEM, sporocilo="Sporocilo0")
		log1 = Log(nivo=LogLevel.ERROR, tema=LogTheme.PROBLEM, sporocilo="Sporocilo1")
		self.assertNotIn(log, log1._povezave)
		self.assertNotIn(log1, log._povezave)
		log.povezi(log1)
		self.assertIn(log, log1._povezave)
		self.assertIn(log1, log._povezave)

	def test_path(self):
		with self.service.transaction() as root:
			kontakti = root.kontakt.path(page=0, max_width=10)
			self.assertEqual(kontakti, root.kontakt[:10])
			self.assertEqual(len(kontakti), 10)
			self.assertIsNotNone(kontakti[0]._povezave[0]._povezave[0]._povezave[0])


if __name__ == '__main__':
	unittest.main()
