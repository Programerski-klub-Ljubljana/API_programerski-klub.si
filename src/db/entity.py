from dataclasses import dataclass
from datetime import datetime
from random import choices, choice
from typing import TypeVar

from persistent import Persistent
from persistent.list import PersistentList

from src.db.enums import LogLevel, LogTheme


class Elist(PersistentList):
	def append(self, item: object):
		for k, v in item.__dict__.items():
			if isinstance(v, list | tuple):
				setattr(item, k, PersistentList(v))
		super(Elist, self).append(item)

	def random(self, k: int = None):
		return choice(self) if k is None else choices(self, k=k)


T = TypeVar('T')
elist = dict[int, T] | Elist


class Entity(Persistent):
	_razred: str = 'Entity'
	_ustvarjen: datetime = datetime.utcnow()
	_posodobljen: datetime = datetime.utcnow()
	_dnevnik: elist = Elist()
	_povezave: elist = Elist()

	@staticmethod
	def save(child: any):
		attr = {
			'_razred': child.__class__.__name__.upper(),
			'_ustvarjen': datetime.utcnow(),
			'_posodobljen': datetime.utcnow(),
			'_dnevnik': Elist(),
			'_povezave': Elist(),
		}
		for k, v in attr.items():
			setattr(child, k, v)

	def povezi(self, entity):
		self._povezave.append(entity)
		entity._povezave.append(self)


@dataclass
class Log(Entity):
	nivo: LogLevel
	tema: LogTheme
	sporocilo: str

	def __post_init__(self):
		Entity.save(self)
