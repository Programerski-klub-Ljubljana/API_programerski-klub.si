import ZODB
from ZODB.DB import ContextManager
from autologging import traced

from app.db import db_seed
from core.domain._entity import Elist
from core.domain.arhitektura_kluba import Oseba
from core.services.db_service import DbService, DbRoot, Transaction


# TODO: Activate me on production! @traced
class ZoDbRoot(DbRoot):
	def __init__(self, root):
		super().__init__()
		for k, v in DbRoot.__annotations__.items():
			value = getattr(root, k, Elist())
			setattr(root, k, value)
			setattr(self, k, value)

	def save(self, *entities, unique=False):
		for entity in entities:
			table = getattr(self, entity.__class__.__name__.lower())
			if unique and entity not in table:  # TODO: Does this works???
				table.append(entity)
			else:
				table.append(entity)

	def oseba_find(self, username: str) -> Oseba:
		for oseba in self.oseba:
			if oseba.has_username(username):
				return oseba


@traced
class ZoDbTransaction(ContextManager, Transaction):

	def __init__(self, db: ZODB.DB, note: str):
		super(ZoDbTransaction, self).__init__(db=db, note=note)

	def __exit__(self, exc_type, exc_value, exc_traceback):
		super(ZoDbTransaction, self).__exit__(t=exc_type, v=exc_value, tb=exc_traceback)

	def __enter__(self) -> ZoDbRoot:
		root = super(ZoDbTransaction, self).__enter__().root
		return ZoDbRoot(root)


@traced
class DbZo(DbService):
	def __init__(self, storage: str, default_password: str):
		self.storage = storage
		self.seeded = False
		self.db = None
		self.default_password = default_password

	def open(self):
		if self.db is not None:
			raise Exception("WTF are you doing?")
		self.db = ZODB.DB(storage=self.storage)

	def seed(self):
		if self.seeded:
			return

		with self.db.transaction(note="seed.migrate") as connection:
			root = ZoDbRoot(connection.root)

			db_seed.arhitektura_kluba(root, geslo=self.default_password, kontakti=10, clani=30, ekipe=10, oddeleki=4, klubi=3)
			db_seed.bancni_racun(root, transakcije=180, bancni_racun=3)
			db_seed.oznanila_sporocanja(root, objave=50, sporocila=90)
			db_seed.srecanja_dogodki_tekme(root, dogodek=20)
			db_seed.vaje_naloge(root, naloge=40, test=10)
			db_seed.logs(root, logs=10)
			db_seed.povezave(root, elementi=10, povezave=5)

		self.seeded = True

	def transaction(self, note: str | None = None) -> ZoDbTransaction:
		if self.db is None:
			raise Exception("WTF are you doing?")
		return ZoDbTransaction(self.db, note)
