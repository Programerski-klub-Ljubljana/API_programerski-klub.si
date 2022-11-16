from dataclasses import dataclass

import ZODB
from transaction import TransactionManager

from app.db import db_seed, db_entities
from core.domain._entity import Elist
from core.domain.arhitektura_kluba import Clan
from core.services.db_service import DbService, Transaction, DbRoot


class ZoDB(DbService):
	def __init__(self, storage: str):
		self.storage = storage
		self.db = None

	def open(self):
		self.db = ZODB.DB(storage=self.storage)

	def seed(self):
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

	def transaction(self, note: str | None = None):
		return ZoDbTransaction(self.db, note=note)

	def get_clan(self, username) -> Clan | None:
		with self.transaction() as root:
			for user in root.clan:
				if user.username == username:
					return user
		return None


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


@dataclass
class ZoDbTransaction(Transaction):
	db: ZODB.DB
	note: str
	manager: TransactionManager = None

	def __enter__(self) -> ZoDbRoot:
		self.manager = TransactionManager()
		connection = self.db.open(self.manager)
		return ZoDbRoot(connection.root)

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.manager.commit()