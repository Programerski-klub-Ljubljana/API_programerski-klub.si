import ZODB
import transaction

from app import env
from app.db import seed
from core.domain._entity import Elist, elist, Log
from core.domain.arhitektura_kluba import Clan, Ekipa, Oddelek, Klub, Kontakt
from core.domain.bancni_racun import Transakcija, Bancni_racun
from core.domain.oznanila_sporocanja import Objava, Sporocilo
from core.domain.srecanja_dogodki import Dogodek
from core.domain.vaje_naloge import Test, Naloga
from core.services.db_service import DbService


class ZoDB(DbService):
	def __init__(self):
		self._db = ZODB.DB(env.DB_PATH)

	def path(self, entity: str, path: str | None = None):
		pass

	def seed(self):
		with self._db.transaction(note="seed.migrate") as con:
			root = Root(con.root)
			seed.arhitektura_kluba(root, kontakti=120, clani=60, ekipe=20, oddeleki=6, klubi=4)
			seed.bancni_racun(root, transakcije=180, bancni_racun=3)
			seed.oznanila_sporocanja(root, objave=50, sporocila=200)
			seed.srecanja_dogodki_tekme(root, dogodek=50)
			seed.vaje_naloge(root, naloge=400, test=30)
			seed.logs(root, logs=50)
			seed.povezave(root, elementi=50, povezave=5)
			print('\nDatabase seeding finished... WAIT FOR TRANSACTION TO FINISH!\n')

	def transaction(self, note: str | None = None):
		return Transaction(self._db, note=note)


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
	def __init__(self, db, note: str = None):
		self.db = db
		self.note = note
		self.manager = None

	def __enter__(self) -> Root:
		self.manager = transaction.TransactionManager()
		connection = self.db.open(self.manager)
		return Root(connection.root)

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.manager.commit()
