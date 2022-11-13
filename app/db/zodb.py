from dataclasses import dataclass

import ZODB
from transaction import TransactionManager

from app import env
from app.db import seed
from core.domain._entity import Elist
from core.services.db_service import DbService, Transaction, DbRoot


class ZoDB(DbService):
	def __init__(self):
		self.db: ZODB.DB = ZODB.DB(env.DB_PATH)

	def seed(self):
		with self.db.transaction(note="seed.migrate") as connection:
			root = ZoDbRoot(connection.root)
			seed.arhitektura_kluba(root, kontakti=60, clani=30, ekipe=10, oddeleki=4, klubi=3)
			seed.bancni_racun(root, transakcije=180, bancni_racun=3)
			seed.oznanila_sporocanja(root, objave=50, sporocila=90)
			seed.srecanja_dogodki_tekme(root, dogodek=20)
			seed.vaje_naloge(root, naloge=40, test=10)
			seed.logs(root, logs=10)
			seed.povezave(root, elementi=10, povezave=5)

	def transaction(self, note: str | None = None):
		return ZoDbTransaction(self.db, note=note)


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
