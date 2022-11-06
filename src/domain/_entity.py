from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar

from persistent import Persistent
from persistent.list import PersistentList

from src.domain._enums import LogLevel, LogTheme


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


class EntityList(PersistentList):
	pass


class Entity(Persistent):
	def __init__(self):
		self._ustvarjen: datetime = datetime.utcnow()
		self._posodobljen: datetime = datetime.utcnow()
		self._dnevnik: Elist
		self._povezave: Elist


class Elist(PersistentList):
	def append(self, item: object):
		print(f"APPEND: {item}")
		for k, v in item.__dict__.items():
			if isinstance(v, list | tuple):
				setattr(item, k, PersistentList(v))
		print('------------')
		super(Elist, self).append(item)

	def update(self):
		self._posodobljen = datetime.utcnow()

	def povezi(self, entity: Entity):
		self._povezave.append(entity)
		entity._povezave.append(self)


T = TypeVar('T')
elist = list[T] | Elist
