import unittest
from random import randint

from persistent.list import PersistentList

from app import APP
from core.domain._entity import Elist, Log
from core.domain._enums import LogLevel, LogType
from core.domain.arhitektura_kluba import Oseba, TipOsebe, Kontakt, TipKontakta, NivoValidiranosti
from core.services.db_service import DbService


class test_db(unittest.TestCase):

	def setUp(self):
		APP.init(seed=False)

		self.service: DbService = APP.services.db()

		# FILL DATABASE...
		with self.service.transaction() as root:
			root.oseba.clear()
			for i in range(10):
				oseba = Oseba(ime=f'ime{i}', priimek=f'priimek{i}', rojen=None, kontakti=[
					Kontakt(data=f'data{i}', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])
				root.save(oseba)

	def tearDown(self):
		with self.service.transaction() as root:
			root.oseba.clear()

	# * TESTING DB SERVICE

	def test_open(self):
		self.assertRaises(Exception, lambda: (self.service.open(), self.service.open()))

	def test_transaction(self):
		new_ime = '12345'

		with self.service.transaction() as root:
			index = randint(0, len(root.oseba) - 1)
			self.assertNotEqual(root.oseba[index].ime, new_ime)
			old_ime = root.oseba[index].ime
			root.oseba[index].ime = new_ime

		with self.service.transaction() as root:
			self.assertEqual(root.oseba[index].ime, new_ime)
			root.oseba[index].ime = old_ime

	def test_find(self):
		oseba = Oseba(ime=f'ime8', priimek=f'priimek8', rojen=None, kontakti=[
			Kontakt(data=f'data8', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])

		count = 0
		for found_oseba in self.service.find(oseba):
			self.assertEqual(found_oseba, oseba)
			count += 1
		self.assertEqual(count, 1)

	def test_oseba_find(self):
		oseba = None
		data = None
		with self.service.transaction() as root:
			oseba = root.oseba[5]
			data = oseba.kontakti[-1].data
			self.assertGreater(len(data), 3)

		for db_oseba in self.service.oseba_find(data):
			self.assertTrue(db_oseba.equal(oseba))
		for db_oseba in self.service.oseba_find(oseba._id):
			self.assertTrue(db_oseba.equal(oseba))

	def test_oseba_find_fail(self):
		count = 0
		for _ in self.service.oseba_find('asdfasfasdf'):
			count += 1
		self.assertEqual(count, 0)

	# * TESTING DB ROOT

	def test_root_properties(self):
		with self.service.transaction() as root:
			self.assertEqual(len(root.oseba), 10)
			self.assertIsInstance(root.oseba, Elist)

	def test_root_save(self):

		with self.service.transaction() as root:
			# CREATE KONTACTS
			clan1 = Oseba(ime='ime1', priimek='priimek', tip_osebe=[TipOsebe.CLAN], rojen=None, kontakti=[
				Kontakt(data="a983joirow34je", tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)
			])
			clan2 = Oseba(ime='ime1', priimek='priimek', tip_osebe=[TipOsebe.CLAN], rojen=None, kontakti=[
				Kontakt(data="0392pep2opo", tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)
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
		with self.service.transaction() as root:
			for clan in root.oseba:
				if clan == clan1:  # TODO: Make this stricter
					clan_find1 = clan
				if clan == clan2:  # TODO: Make this stricter
					clan_find2 = clan

			# TEST IF FOUND EQUAL TO INSERTED
			self.assertTrue(clan_find1.equal(clan1))
			self.assertTrue(clan_find2.equal(clan2))

			# TEST IF LIST ARE CONVERTE TO PERSISTENT LISTS
			self.assertIsInstance(clan_find1.vpisi, PersistentList)
			self.assertIsInstance(clan_find2.vpisi, PersistentList)

			# TEST IF LIST ARE CONVERTE TO PERSISTENT LISTS
			self.assertIsInstance(clan1.vpisi, PersistentList)
			self.assertIsInstance(clan2.vpisi, PersistentList)

	def test_root_save_unique(self):
		with self.service.transaction() as root:
			root.oseba.clear()

			# CREATE KONTACTS
			clan1 = Oseba(ime='ime1', priimek='priimek', tip_osebe=[TipOsebe.CLAN], rojen=None, kontakti=[
				Kontakt(data="a983joirow34je", tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])

			root.save(clan1, clan1, clan1, unique=True)

			self.assertEqual(len(root.oseba), 1)

	def test_logs(self):
		with self.service.transaction() as root:
			root.oseba[0].ime = 'ime'
			root.oseba[0].tip_osebe.append('append')
			root.oseba[0].tip_osebe[0] = 'setitem'
			root.oseba[0].tip_osebe += ['add']
			root.oseba[0].tip_osebe *= 2
			root.oseba[0].log(type=LogType.ENTITY, level=LogLevel.DEBUG, msg='msg')
			root.oseba[0].log_call(self.test_logs, kwargs={'arg0': 'arg0', 'arg1': 'arg2'})
			root.oseba[0].log_info(type=LogType.ENTITY, msg='msg')
			root.oseba[0].log_error(type=LogType.ENTITY, msg='msg')

		with self.service.transaction() as root:
			self.assertEqual(root.oseba[0].logs, [
				Log(level=LogLevel.DEBUG, type=LogType.ENTITY,
				    msg='__init__(ime="ime0", priimek="priimek0", rojen=None, geslo=None, tip_osebe=[], '
				        "kontakti=[Kontakt(data='data0', tip=<TipKontakta.EMAIL: 'EMAIL'>, nivo_validiranosti=<NivoValidiranosti.POTRJEN: 'POTRJEN'>)], "
				        "vpisi=[], izpisi=[])"),
				Log(level=LogLevel.DEBUG, type=LogType.ENTITY,
				    msg="kontakti = [Kontakt(data='data0', tip=<TipKontakta.EMAIL: 'EMAIL'>, nivo_validiranosti=<NivoValidiranosti.POTRJEN: 'POTRJEN'>)]"),
				Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='ime = "ime"'),
				Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='tip_osebe.append(item="append")'),
				Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='tip_osebe.__setitem__(i=0, item="setitem")'),
				Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="tip_osebe.__iadd__(other=['add'])"),
				Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="tip_osebe = ['setitem', 'add']"),
				Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='tip_osebe.__imul__(other=2)'),
				Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="tip_osebe = ['setitem', 'add', 'setitem', 'add']"),
				Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg'),
				Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='test_logs(arg0="arg0", arg1="arg2")'),
				Log(level=LogLevel.INFO, type=LogType.ENTITY, msg='msg'),
				Log(level=LogLevel.ERROR, type=LogType.ENTITY, msg='msg')
			])

			self.assertEqual(root.oseba[0].tip_osebe, ['setitem', 'add', 'setitem', 'add'])


if __name__ == '__main__':
	unittest.main()
