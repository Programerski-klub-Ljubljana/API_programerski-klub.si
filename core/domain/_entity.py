from dataclasses import dataclass, field
from datetime import datetime
from random import choices, choice
from typing import TypeVar

from persistent import Persistent
from persistent.list import PersistentList

from core import cutils
from core.domain._enums import LogLevel, LogTheme


class Elist(PersistentList):
	def __contains__(self, item):
		for ele in self:
			if ele == item:
				return True
		return False

	def append(self, item: object):
		if cutils.is_object(item):
			for k, v in item.__dict__.items():
				if isinstance(v, list | tuple):
					setattr(item, k, PersistentList(v))
		super(Elist, self).append(item)

	def random(self, k: int = None):
		return choice(self) if k is None else choices(self, k=k)

	def path(
			self,
			path: str | None = None,
			page: int = 0,
			max_width: int = 10) -> any:

		result = cutils.object_path(self, path)
		start = max_width * page
		end = max_width * (page + 1)
		return result[start:end] if cutils.is_iterable(result) else result

	@staticmethod
	def field(*values: any):
		return field(default_factory=lambda: Elist(values))


T = TypeVar('T')
elist = list[T] | Elist


class Entity(Persistent):
	_razred: str = 'Entity'
	_ustvarjen: datetime = datetime.utcnow()
	_posodobljen: datetime = datetime.utcnow()
	_dnevnik: elist = Elist.field()
	_povezave: elist = Elist.field()

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

	def povezi(self, *entity):
		for e in entity:
			self._povezave.append(e)
			e._povezave.append(self)


@dataclass
class Log(Entity):
	nivo: LogLevel
	tema: LogTheme
	sporocilo: str

	def __post_init__(self):
		Entity.save(self)
