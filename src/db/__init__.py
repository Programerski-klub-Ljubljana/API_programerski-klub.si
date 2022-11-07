from contextlib import contextmanager
from typing import Iterator

import ZODB.FileStorage

from src.db.entity import Plist, plist, Log, Povezava
from src.domain.arhitektura_kluba import Clan, Ekipa, Oddelek, Klub, Kontakt
from src.domain.bancni_racun import Transakcija, BancniRacun
from src.domain.oznanila_sporocanja import Objava, Sporocilo
from src.domain.srecanja_dogodki import Dogodek
from src.domain.vaje_naloge import Test, Naloga

_db = ZODB.DB(None)


class Root:
	logs: plist[Log]
	povezave: plist[Povezava]

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


@contextmanager
def transaction(note: str = None) -> Iterator[Root]:
	with _db.transaction(note=note) as con:
		yield Root(con.root)
