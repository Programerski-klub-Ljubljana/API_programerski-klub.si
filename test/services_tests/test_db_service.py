import unittest
from datetime import datetime

from persistent.list import PersistentList

from app import APP
from app.db import db_entities
from core.domain._entity import Elist, Log
from core.domain._enums import LogTheme, LogLevel


class test_db(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)

		# TEST IF EMPTY
		count = 0
		with APP.db.transaction() as root:
			print(type(root))
			for k, v in root.__dict__.items():
				if isinstance(v, Elist):
					count += 1
					assert len(v) == 0 and isinstance(v, Elist)
		assert count > 0

		APP.db.seed()

	def test_transaction(self):
		count = 0
		with APP.db.transaction() as root:
			for k, v in root.__dict__.items():
				count += 1
				self.assertGreater(len(v), 0, k)
				self.assertIsInstance(v, Elist)
		self.assertGreater(count, 0)

	def test_entity_properties(self):
		with APP.db.transaction() as root:
			k = root.clan[0]
			self.assertEqual(k._razred, 'CLAN')
			self.assertLessEqual(k._ustvarjen, datetime.utcnow())
			self.assertLessEqual(k._posodobljen, datetime.utcnow())
			self.assertGreaterEqual(len(k._dnevnik), 0)
			self.assertGreaterEqual(len(k._povezave), 0)

	def test_transaction_change(self):
		ime = 'ime'
		with APP.db.transaction() as root:
			self.assertNotEqual(root.clan[0].ime, ime)
			root.clan[0].ime = ime

		with APP.db.transaction() as root:
			self.assertEqual(root.clan[0].ime, ime)

	def test_transaction_save_append(self):

		with APP.db.transaction() as root:
			# CREATE KONTACTS
			clan1 = db_entities.init_clan(ime='ime1')
			clan2 = db_entities.init_clan(ime='ime2')

			# ARE THEY EQUAL?
			self.assertNotEqual(clan2, clan1)

			# TEST IF LIST ARE NOT YET CONVERTED TO PERSISTENT LISTS
			self.assertNotIsInstance(clan1.vpisi, PersistentList)
			self.assertNotIsInstance(clan2.vpisi, PersistentList)

			# TEST IF KONTACTS NOT EXISTS IN DB
			assert clan1 not in root.clan
			assert clan2 not in root.clan

			# INSERT NEW CONTACTS
			root.save(clan1, clan2)

		# FIND CONTACTS
		# clan_find1 = None
		# clan_find2 = None

		# with APP.db.transaction() as root:
		# 	for clan in root.clan:
		# 		if clan == clan1:
		# 			clan_find1 = clan
		# 		if clan == clan2:
		# 			clan_find2 = clan
		#
		# 	TEST IF FOUND EQUAL TO INSERTED
			# self.assertEqual(clan_find1, clan1)
			# self.assertEqual(clan_find2, clan2)
			#
			# TEST IF LIST ARE CONVERTE TO PERSISTENT LISTS
			# self.assertIsInstance(clan_find1.vpisi, PersistentList)
			# self.assertIsInstance(clan_find2.vpisi, PersistentList)
			#
			# TEST IF LIST ARE CONVERTE TO PERSISTENT LISTS
			# self.assertIsInstance(clan1.vpisi, PersistentList)
			# self.assertIsInstance(clan2.vpisi, PersistentList)

	def test_transaction_random_0(self):
		with APP.db.transaction() as root:
			clan1 = root.clan.random()
			clan2 = root.clan.random()
			self.assertNotEqual(clan1, clan2)
			self.assertIn(clan1, root.clan)
			self.assertIn(clan2, root.clan)
			self.assertNotEqual(root.clan.index(clan1), root.clan.index(clan2))

	def test_transaction_random_1(self):
		with APP.db.transaction() as root:
			clani = root.clan.random(k=3)
			self.assertTrue(clani[0] != clani[1] != clani[2])
			for k in clani:
				self.assertIn(k, root.clan)

	def test_povezi(self):
		log = Log(nivo=LogLevel.ERROR, tema=LogTheme.PROBLEM, sporocilo="Sporocilo0")
		log1 = Log(nivo=LogLevel.ERROR, tema=LogTheme.PROBLEM, sporocilo="Sporocilo1")
		self.assertNotIn(log, log1._povezave)
		self.assertNotIn(log1, log._povezave)
		log.povezi(log1)
		self.assertIn(log, log1._povezave)
		self.assertIn(log1, log._povezave)

	def test_path(self):
		with APP.db.transaction() as root:
			kontakti = root.clan.path(page=0, max_width=10)
			self.assertEqual(kontakti, root.clan[:10])
			self.assertEqual(len(kontakti), 10)
			self.assertIsNotNone(kontakti[0]._povezave[0]._povezave[0]._povezave[0])


if __name__ == '__main__':
	unittest.main()
