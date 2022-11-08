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
	p_razred: str = 'Entity'
	p_ustvarjen: datetime = datetime.utcnow()
	p_posodobljen: datetime = datetime.utcnow()
	p_dnevnik: elist = Elist()
	p_povezave: elist = Elist()

	@staticmethod
	def save(child: any):
		attr = {
			'p_razred': child.__class__.__name__.upper(),
			'p_ustvarjen': datetime.utcnow(),
			'p_posodobljen': datetime.utcnow(),
			'p_dnevnik': Elist(),
			'p_povezave': Elist(),
		}
		for k, v in attr.items():
			setattr(child, k, v)

	def povezi(self, entity):
		self.p_povezave.append(entity)
		entity.p_povezave.append(self)


@dataclass
class Log(Entity):
	nivo: LogLevel
	tema: LogTheme
	sporocilo: str

	def __post_init__(self):
		self.entity: Entity = Entity(self)
