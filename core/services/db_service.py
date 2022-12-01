from abc import ABC, abstractmethod

from core.domain._entity import elist, Log, Entity
from core.domain.arhitektura_kluba import Oseba, Ekipa, Oddelek, Klub
from core.domain.bancni_racun import Transakcija, Bancni_racun
from core.domain.oznanila_sporocanja import Objava, Sporocilo
from core.domain.srecanja_dogodki import Dogodek
from core.domain.vaje_naloge import Test, Naloga


class DbRoot(ABC):
	log: elist[Log]
	klub: elist[Klub]
	oseba: elist[Oseba]
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
	def save(self, *entities, unique=False):
		pass

	@abstractmethod
	def oseba_find(self, kontakt_data) -> Oseba | None:
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
	def find(self, entity: Entity) -> list[Entity]:
		pass
