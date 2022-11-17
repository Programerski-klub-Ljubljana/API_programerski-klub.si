from dataclasses import dataclass

import ZODB
from ZODB.DB import ContextManager
from autologging import traced

from app.db import db_seed
from core.domain._entity import Elist
from core.domain.arhitektura_kluba import Clan
from core.services.db_service import DbService, DbRoot


# TODO: Activate me on production! @traced
class ZoDbRoot(DbRoot):
	def __init__(self, root):
		super().__init__()
		for k, v in DbRoot.__annotations__.items():
			value = getattr(root, k, Elist())
			setattr(root, k, value)
			setattr(self, k, value)

	def save(self, *entities):
		for entity in entities:
			getattr(self, entity.__class__.__name__.lower()).append(entity)

	def get_clan(self, username) -> Clan | None:
		for user in self.clan:
			if user.username == username:
				return user
		return None


@traced
@dataclass
class ZoDbTransaction(ContextManager):
	def __init__(self, db: ZODB.DB, note: str):
		super(ZoDbTransaction, self).__init__(db=db, note=note)

	def __enter__(self) -> ZoDbRoot:
		root = super(ZoDbTransaction, self).__enter__().root
		return ZoDbRoot(root)


@traced
class ZoDB(DbService):
	def __init__(self, storage: str):
		self.storage = storage
		self.seeded = False
		self.db = None

	def open(self):
		if self.db is not None:
			raise Exception("WTF are you doing?")
		self.db = ZODB.DB(storage=self.storage)

	def seed(self):
		if self.seeded:
			return

		with self.db.transaction(note="seed.migrate") as connection:
			root = ZoDbRoot(connection.root)

			db_seed.entities(root)
			db_seed.arhitektura_kluba(root, kontakti=60, clani=30, ekipe=10, oddeleki=4, klubi=3)
			db_seed.bancni_racun(root, transakcije=180, bancni_racun=3)
			db_seed.oznanila_sporocanja(root, objave=50, sporocila=90)
			db_seed.srecanja_dogodki_tekme(root, dogodek=20)
			db_seed.vaje_naloge(root, naloge=40, test=10)
			db_seed.logs(root, logs=10)
			db_seed.povezave(root, elementi=10, povezave=5)

		self.seeded = True

	def transaction(self, note: str | None = None) -> ZoDbTransaction:
		return ZoDbTransaction(self.db, note)
