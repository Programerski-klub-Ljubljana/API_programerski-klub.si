from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar

from persistent import Persistent
from persistent.list import PersistentList

from src.db.enums import LogLevel, LogTheme


class Plist(PersistentList):
	def append(self, item: object):
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

	def __repr__(self):
		return f'Entity(ustvarjen={self.ustvarjen}, posodobljen={self.posodobljen}, dnevnik={len(self.dnevnik)}, povezave={len(self.povezave)})'

	def povezi(self, povezava, entity):
		self.entity.povezave.append(povezava)
		entity.entity.povezave.append(povezava)


@dataclass
class Log(Entity):
	nivo: LogLevel
	tema: LogTheme
	sporocilo: str

	def __post_init__(self):
		self.entity: Entity = Entity()


@dataclass
class Povezava(Entity):
	ime: str
	opis: str
	jakost: float
	child: Entity
	parent: Entity

	def __post_init__(self):
		self.entity: Entity = Entity()
		self.child_type: str = self.child.__class__.__name__
		self.parent_type: str = self.parent.__class__.__name__
