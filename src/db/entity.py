from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar

from persistent import Persistent
from persistent.list import PersistentList

from src.db.enums import LogLevel, LogTheme


class Plist(PersistentList):
	def append(self, item: object):
		item.entity.razred = item.__class__.__name__.upper()
		for k, v in item.__dict__.items():
			if isinstance(v, list | tuple):
				setattr(item, k, PersistentList(v))
		super(Plist, self).append(item)

	def update(self):
		self.entity.posodobljen = datetime.utcnow()


T = TypeVar('T')
plist = list[T] | Plist


@dataclass
class Entity(Persistent):
	def __init__(self):
		self.ustvarjen: datetime = datetime.utcnow()
		self.posodobljen: datetime = datetime.utcnow()
		self.dnevnik: Plist = Plist()
		self.povezave: Plist = Plist()

	def povezi(self, entity):
		self.povezave.append(entity)
		entity.povezave.append(self)


@dataclass
class Log(Entity):
	nivo: LogLevel
	tema: LogTheme
	sporocilo: str

	def __post_init__(self):
		self.entity: Entity = Entity(self)
