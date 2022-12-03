import ZODB
from ZODB.DB import ContextManager
from autologging import traced

from app.db import db_seed
from core.domain._entity import Elist, Entity
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

	def save(self, *entities: Entity, unique=False):
		for entity in entities:
			table = getattr(self, entity.type)
			if unique and entity not in table:  # TODO: Does this works???
				table.append(entity)
			elif not unique:
				table.append(entity)


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

	def find(self, entity: Entity) -> list[Entity]:
		# PREVERI MOZNO DUPLIKACIJO PODATKOV!
		entity_type = entity.type
		with self.transaction(note=f'Find {entity}') as root:
			table = getattr(root, entity_type, None)
			for old_entity in table:
				if old_entity.equal(entity):
					yield old_entity

	def oseba_find(self, kontakt_data: str) -> list[Oseba]:
		with self.transaction(note=f'Find oseba {kontakt_data}') as root:
			for oseba in root.oseba:
				if oseba.has_kontakt_data(kontakt_data):
					yield oseba
