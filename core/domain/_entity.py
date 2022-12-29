import logging
from dataclasses import dataclass, field
from datetime import datetime
from random import choices, choice
from typing import TypeVar, Callable

import shortuuid
from persistent import Persistent
from persistent.list import PersistentList

from core import cutils
from core.domain._enums import LogLevel, LogTheme

log = logging.getLogger(__name__)


class Elist(PersistentList):
	def __init__(self, data: list[any] = None, logs: bool = True):
		if logs:
			self._logs = Elist(None, logs=False)
		super().__init__(data)

	def _debug(self, method: Callable, locals: dict[str, any] = None):
		print(method)
		if locals is None:
			locals = {}
		if hasattr(self, '_logs'):
			if 'self' in locals: del locals['self']
			kwargs_str = ', '.join([f'{v}' for k, v in locals.items() if not k.startswith('__')])
			log_obj = Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg=f'{method.__name__}({kwargs_str})')
			log.debug(f'{log_obj.msg}')
			self._logs.append(log_obj)

	def __setitem__(self, i, item):
		self._debug(self.__setitem__, locals())
		super(Elist, self).__setitem__(i, item)

	def __delitem__(self, i):
		self._debug(self.__delitem__, locals())
		super(Elist, self).__delitem__(i)

	def __iadd__(self, elist):
		self._debug(self.__iadd__, locals())
		super(Elist, self).__iadd__(elist)

	def __imul__(self, elist):
		self._debug(self.__imul__, locals())
		super(Elist, self).__imul__(elist)

	def __contains__(self, item):
		for ele in self:
			if isinstance(ele, Entity):
				if ele.equal(item):
					return True
			elif ele == item:
				return True
		return False

	def clear(self):
		self._debug(self.clear)
		super(Elist, self).clear()

	def insert(self, i, item):
		self._debug(self.insert, locals())
		super(Elist, self).insert(i, item)

	def pop(self, i=-1):
		self._debug(self.pop, locals())
		super(Elist, self).pop(i)

	def remove(self, item):
		self._debug(self.remove, locals())
		super(Elist, self).remove(item)

	def reverse(self):
		self._debug(self.reverse, locals())
		super(Elist, self).reverse()

	def sort(self, *args, **kwargs):
		self._debug(self.sort, locals())
		super(Elist, self).sort(*args, **kwargs)

	def append(self, item: object):
		self._debug(self.append, locals())
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
		return field(default_factory=lambda: Elist(list(values)))


T = TypeVar('T')
elist = list[T] | Elist


class Entity(Persistent):
	_id: str | None
	_type: str | None
	_created: datetime | None
	_updated: datetime | None
	_logs: elist | None
	_connections: elist | None

	def __post_init__(self):
		attr = {
			'_id': shortuuid.uuid(),
			'_type': self.type.upper(),
			'_created': datetime.now(),
			'_updated': datetime.now(),
			'_connections': Elist(),
			'_logs': Elist(),
		}
		for k, v in attr.items():
			setattr(self, k, v)

	def __setattr__(self, key, value):
		if not isinstance(self, Log):
			if hasattr(self, '_logs'):
				self._debug(key, value)
		self.__dict__[key] = value

	def _debug(self, key, value):
		log_obj = Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg=f'{key} = {value}')
		log.debug(f'{log_obj.msg} ... {self}')
		self._logs.append(log_obj)

	@property
	def type(self):
		return self.__class__.__name__.lower()

	# TODO: Make this abstract
	def equal(self, entity):
		return self == entity

	def merge(self, locals: dict[str, any]):
		del locals['self']
		kwargs_str = ', '.join([f'{v}' for k, v in locals.items() if not k.startswith('__')])
		log_obj = Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg=f'{self.merge.__name__}({kwargs_str})')
		log.debug(f'{log_obj.msg}')
		self._logs.append(log_obj)

	def connect(self, *entity):
		log_obj = Log(level=LogLevel.INFO, theme=LogTheme.SPREMEMBA, msg=f'{self.connect.__name__}({[str(e) for e in entity]})')
		log.debug(f'{log_obj.msg} ... {self}')
		self._logs.append(log_obj)

		for e in entity:
			if e not in self._connections:
				self._connections.append(e)
			if self not in e._connections:
				e._connections.append(self)


@dataclass
class Log(Entity):
	level: LogLevel
	theme: LogTheme
	msg: str
