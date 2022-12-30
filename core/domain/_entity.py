import logging
from copy import copy
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

	def _log_call(self, method: Callable, kwargs: dict[str, any] = None):
		if kwargs is None:
			kwargs = {}
		if hasattr(self, '_logs'):
			if 'self' in kwargs: del kwargs['self']
			kwargs_str = ', '.join([f'{k}=' + (f'"{v}"' if isinstance(v, str) else str(v)) for k, v in kwargs.items() if not k.startswith('__')])
			log_obj = Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg=f'{method.__name__}({kwargs_str})')
			log.debug(log_obj.msg)
			self._logs.append(log_obj)

	def __setitem__(self, i, item):
		self._log_call(self.__setitem__, locals())
		super(Elist, self).__setitem__(i, item)

	def __add__(self, other):
		self._log_call(self.__add__, locals())
		return super(Elist, self).__add__(other)

	def __radd__(self, other):
		self._log_call(self.__radd__, locals())
		return super(Elist, self).__radd__(other)

	def __iadd__(self, other):
		self._log_call(self.__iadd__, locals())
		return super(Elist, self).__iadd__(other)

	def __mul__(self, other):
		self._log_call(self.__mul__, locals())
		return super(Elist, self).__mul__(other)

	def __rmul__(self, other):
		self._log_call(self.__rmul__, locals())
		return super(Elist, self).__rmul__(other)

	def __imul__(self, other):
		self._log_call(self.__imul__, locals())
		return super(Elist, self).__imul__(other)

	def __contains__(self, item):
		for ele in self:
			if isinstance(ele, Entity):
				if ele.equal(item):
					return True
			elif ele == item:
				return True
		return False

	def append(self, item: object):
		self._log_call(self.append, locals())
		if cutils.is_object(item):
			for k, v in item.__dict__.items():
				if isinstance(v, list | tuple):
					setattr(item, k, PersistentList(v))
		super(Elist, self).append(item)

	def clear(self):
		self._log_call(self.clear)
		super(Elist, self).clear()

	def insert(self, i, item):
		self._log_call(self.insert, locals())
		super(Elist, self).insert(i, item)

	def pop(self, i=-1):
		self._log_call(self.pop, locals())
		return super(Elist, self).pop(i)

	def remove(self, item):
		self._log_call(self.remove, locals())
		super(Elist, self).remove(item)

	def reverse(self):
		self._log_call(self.reverse, locals())
		super(Elist, self).reverse()

	def sort(self, *args, **kwargs):
		self._log_call(self.sort, locals())
		super(Elist, self).sort(*args, **kwargs)

	def extend(self, other):
		self._log_call(self.extend, locals())
		super(Elist, self).extend(other)

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
			'_type': self.__class__.__name__.lower(),
			'_created': datetime.now(),
			'_updated': datetime.now(),
			'_connections': Elist(),
			'_logs': Elist(logs=False),
		}
		for k, v in attr.items():
			setattr(self, k, v)

	def __setattr__(self, key, value):
		if not isinstance(self, Log):
			if hasattr(self, '_logs'):
				value_str = f'"{value}"' if isinstance(value, str) else str(value)
				log_obj = Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg=f'{key} = {value_str}')
				log.debug(f'{log_obj.msg} ... {self}')
				self._logs.append(log_obj)
		self.__dict__[key] = value

	def __delattr__(self, item):
		raise Exception("Not allowed!")

	@property
	def logs(self):
		lgs = copy(self._logs)
		for k, v in self.__dict__.items():
			if hasattr(v, '_logs'):
				for l in copy(v._logs):
					l.msg = f'{k}.{l.msg}'
					lgs.append(l)
		return sorted(lgs, key=lambda l: l._created)

	def log_call(self, method: Callable, kwargs):
		if 'self' in kwargs: del kwargs['self']
		kwargs_str = ', '.join([f'{k}=' + (f'"{v}"' if isinstance(v, str) else str(v)) for k, v in kwargs.items() if not k.startswith('__')])
		log_obj = Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg=f'{method.__name__}({kwargs_str})')
		log.debug(f'{log_obj.msg} ... {self}')
		self._logs.append(log_obj)

	def equal(self, entity):
		return self == entity

	def connect(self, *entity):
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
