from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Union

from faker import Faker
from faker.providers import address, company, date_time, internet, person, phone_number, ssn
from persistent import Persistent
from persistent.list import PersistentList


class EntityEnum(str, Enum):
	def _generate_next_value_(self, start, count, last_values):
		return self

	@classmethod
	def values(cls) -> list[str]:
		return list(map(lambda c: c.value, cls))


class PList(PersistentList):
	def append(self, item: object):
		for k, v in item.__dict__.items():
			if isinstance(v, list | tuple):
				setattr(item, k, PersistentList(v))
		super(PList, self).append(item)


class LogLevel(EntityEnum):
	DEBUG = auto()
	INFO = auto()
	WARNING = auto()
	ERROR = auto()


class LogTheme(EntityEnum):
	OSNOVNOSOLSKI = auto()
	SREDNJESOLSKI = auto()
	GITHUB = auto()
	PREKRSEK = auto()
	PROBLEM = auto()


@dataclass
class Log(Persistent):
	nivo: LogLevel
	tema: LogTheme
	sporocilo: str
	_ustvarjen: datetime = datetime.utcnow()


@dataclass
class Povezava(Persistent):
	nivo: LogLevel
	tema: LogTheme
	sporocilo: str
	_ustvarjen: datetime = datetime.utcnow()


@dataclass
class Entity:
	_povezave: list


class Entity(Persistent):
	def __init__(self, child):
		self._ustvarjen: datetime = datetime.utcnow()
		self._posodobljen: datetime = datetime.utcnow()
		self._dnevnik: list[Log] = PersistentList()
		self._povezave: list[Entity] = PersistentList()

	def update(self):
		self._posodobljen = datetime.utcnow()

	def povezi(self, entity: Entity):
		self._povezave.append(entity)
		entity._povezave.append(self)
