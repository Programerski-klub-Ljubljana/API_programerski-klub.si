import sys

import ZODB.FileStorage
import transaction

from src import env
from src.db.entity import Elist, elist, Log
from src.domain.arhitektura_kluba import Clan, Ekipa, Oddelek, Klub, Kontakt
from src.domain.bancni_racun import Transakcija, Bancni_racun
from src.domain.oznanila_sporocanja import Objava, Sporocilo
from src.domain.srecanja_dogodki import Dogodek
from src.domain.vaje_naloge import Test, Naloga

_db = ZODB.DB(env.DB_PATH)


class Root:
	log: elist[Log]
	klub: elist[Klub]
	kontakt: elist[Kontakt]
	clan: elist[Clan]
	ekipa: elist[Ekipa]
	oddelek: elist[Oddelek]
	transakcija: elist[Transakcija]
	bancni_racun: elist[Bancni_racun]
	objava: elist[Objava]
	sporocilo: elist[Sporocilo]
	dogodek: elist[Dogodek]
	test: elist[Test]
	naloga: elist[Naloga]

	def __init__(self, root):
		for k, v in Root.__annotations__.items():
			value = getattr(root, k, Elist())
			setattr(root, k, value)
			setattr(self, k, value)

	def save(self, *entities):
		for entity in entities:
			getattr(self, entity.__class__.__name__.lower()).append(entity)


class Transaction:
	def __init__(self, note: str = None):
		self.note = note
		self.manager = None

	def __enter__(self) -> Root:
		self.manager = transaction.TransactionManager()
		connection = _db.open(self.manager)
		return Root(connection.root)

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.manager.commit()
