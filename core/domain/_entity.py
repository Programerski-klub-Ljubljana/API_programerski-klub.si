from dataclasses import dataclass, field
from datetime import datetime
from random import choices, choice
from typing import TypeVar

import shortuuid
from persistent import Persistent
from persistent.list import PersistentList

from core import cutils
from core.domain._enums import LogLevel, LogTheme


class Elist(PersistentList):
	def __contains__(self, item):
		for ele in self:
			if isinstance(ele, Entity):
				if ele.equal(item):
					return True
			elif ele == item:
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
	_id: str | None
	_type: str | None
	_created: datetime | None
	_updated: datetime | None
	_logs: elist | None
	_connections: elist | None

	@property
	def type(self):
		return self.__class__.__name__.lower()

	def connect(self, *entity):
		for e in entity:
			if e not in self._connections:
				self._connections.append(e)
			if self not in e._connections:
				e._connections.append(self)

	# TODO: Make this abstract
	def equal(self, entity):
		return self == entity

	def merge(self, *args, **kwargs):
		raise Exception("Implement me!")

	def __post_init__(self):
		attr = {
			'_id': shortuuid.uuid(),
			'_type': self.type.upper(),
			'_created': datetime.now(),
			'_updated': datetime.now(),
			'_logs': Elist(),
			'_connections': Elist(),
		}
		for k, v in attr.items():
			setattr(self, k, v)


@dataclass
class Log(Entity):
	level: LogLevel
	theme: LogTheme
	msg: str
