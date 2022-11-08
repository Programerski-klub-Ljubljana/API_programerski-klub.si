import ZODB.FileStorage
import transaction

from src.db.entity import Plist, plist, Log
from src.domain.arhitektura_kluba import Clan, Ekipa, Oddelek, Klub, Kontakt
from src.domain.bancni_racun import Transakcija, BancniRacun
from src.domain.oznanila_sporocanja import Objava, Sporocilo
from src.domain.srecanja_dogodki import Dogodek
from src.domain.vaje_naloge import Test, Naloga

_db = ZODB.DB(None)


class Root:
	logs: plist[Log]

	klubi: plist[Klub]
	kontakti: plist[Kontakt]
	clani: plist[Clan]
	ekipe: plist[Ekipa]
	oddelki: plist[Oddelek]
	transakcije: plist[Transakcija]
	bancni_racun: plist[BancniRacun]
	objava: plist[Objava]
	sporocilo: plist[Sporocilo]
	dogodki: plist[Dogodek]
	testi: plist[Test]
	naloge: plist[Naloga]

	def __init__(self, root):
		for k, v in Root.__annotations__.items():
			value = getattr(root, k, Plist())
			setattr(root, k, value)
			setattr(self, k, value)

	def append(self, entity: object):
		for k, v in Root.__annotations__.items():
			print(k, v)



class Transaction:
	def __init__(self, note: str = None):
		self.note = note
		self.manager = None

	def __enter__(self) -> Root:
		print('enter method called')
		self.manager = transaction.TransactionManager()
		connection = _db.open(self.manager)
		return Root(connection.root)

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.manager.commit()
