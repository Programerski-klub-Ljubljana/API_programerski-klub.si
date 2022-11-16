from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.domain._entity import elist, Entity, Log
from core.domain.arhitektura_kluba import Clan, Ekipa, Oddelek, Klub, Kontakt
from core.domain.bancni_racun import Transakcija, Bancni_racun
from core.domain.oznanila_sporocanja import Objava, Sporocilo
from core.domain.srecanja_dogodki import Dogodek
from core.domain.vaje_naloge import Test, Naloga


@dataclass
class DbError(Exception):
	info: str


class DbRoot(ABC):
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

	@abstractmethod
	def save(self, *entities: list[Entity]):
		pass


class Transaction(ABC):
	@abstractmethod
	def __enter__(self) -> DbRoot:
		pass

	@abstractmethod
	def __exit__(self, exc_type, exc_value, exc_traceback):
		pass


class DbService(ABC):

	@abstractmethod
	def open(self):
		pass

	@abstractmethod
	def transaction(self, note: str | None = None) -> Transaction:
		pass

	@abstractmethod
	def seed(self):
		pass

	@abstractmethod
	def get_clan(self, username) -> Clan | None:
		pass
