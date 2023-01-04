from copy import deepcopy
from dataclasses import field, dataclass
from datetime import datetime
from random import choice, choices
from typing import Callable, TypeVar

import shortuuid
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

from core import cutils
from core.domain._enums import LogLevel, LogType


class Elog:
	_p_log: bool = True
	_logs: 'Elist'

	@staticmethod
	def init(data: any, logs: bool):
		if isinstance(data, list | tuple | set):
			data = list(data)
			iterator = enumerate(data)
		elif isinstance(data, dict):
			iterator = data.items()
		else:
			return data

		for k, v in iterator:
			if isinstance(v, list | tuple | set):
				data[k] = Elist(data=list(v), logs=logs)
			elif isinstance(v, dict):
				data[k] = Edict(data=v, logs=logs)

		return data

	@property
	def is_logging(self) -> bool:
		return hasattr(self, '_logs') and self._p_log

	@property
	def logs(self):
		# GETS LOGS 1 LEVEL DEEP
		iterator = []
		key_formator = lambda key: key
		match self.log_type:
			case LogType.EDICT:
				iterator = self.data.items()
				key_formator = lambda key: f"['{key}']"
			case LogType.ELIST:
				iterator = enumerate(self.data)
				key_formator = lambda key: f"[{key}]"
			case LogType.ENTITY:
				iterator = self.data.__dict__.items()
				key_formator = lambda key: f'{key}'

		lgs = deepcopy(self._logs)
		for k, v in iterator:
			if k not in ['_logs'] and hasattr(v, '_logs'):  # ! IGNORE LOGS IN _LOGS
				for l in deepcopy(v._logs):  # ! ORIGINALNIH LOGOV SE NE SME SPREMINJATI!
					if l.type not in [LogType.EDICT_INIT, LogType.ELIST_INIT, LogType.ENTITY_INIT]:  # ! IGNORE INIT LOGS IN SECOND LEVEL.
						l.msg = f'{key_formator(k)}.{l.msg}'
						lgs.append(l)
		return sorted(lgs, key=lambda l: l._created)

	@property
	def log_type(self) -> LogType:
		type_map = {
			Edict: LogType.EDICT,
			Elist: LogType.ELIST,
			Entity: LogType.ENTITY,
			Elog: LogType.ENTITY,
		}

		for cls, typ in type_map.items():
			if isinstance(self, cls):
				return typ

	def log(self, level: LogLevel, type: LogType, msg: str, **kwargs):
		if self.is_logging:
			# ! ZA LOGS DATA JE POTREBNO NAREDITI KOPIJE SAJ NOCES DA PROGRAM MODIFICIRA LOGE MED IZVAJANJEM
			log_obj = Log(level=level, type=type, msg=msg, data=Edict(data=deepcopy(kwargs), logs=False))
			self._logs.append(log_obj)

	def _log_call(self, method: Callable, **kwargs):
		self.log_call(method=method, type=self.log_type, **kwargs)

	def log_call(self, method: Callable, type: LogType, **kwargs):
		self.log(level=LogLevel.DEBUG, type=type, msg=f'{method.__name__}({cutils.kwargs_str(**kwargs)})', **kwargs)

	def log_debug(self, type: LogType, msg: str, **kwargs):
		self.log(level=LogLevel.DEBUG, type=type, msg=msg, **kwargs)

	def log_info(self, type: LogType, msg: str, **kwargs):
		self.log(level=LogLevel.INFO, type=type, msg=msg, **kwargs)

	def log_warning(self, type: LogType, msg: str, **kwargs):
		self.log(level=LogLevel.WARNING, type=type, msg=msg, **kwargs)

	def log_error(self, type: LogType, msg: str, **kwargs):
		self.log(level=LogLevel.ERROR, type=type, msg=msg, **kwargs)


class Edict(Elog, PersistentMapping):

	@staticmethod
	def field(data: dict = {}, logs: bool = True):
		return field(default_factory=lambda: Edict(data=data, logs=logs))

	def __init__(self, data: dict, logs: bool = True):
		data = self.init(data=data, logs=logs)

		super(Edict, self).__init__(data)

		if logs:
			self._logs = Elist(logs=False)
			self.log_call(method=self.__init__, type=LogType.EDICT_INIT, **data)

	def __setitem__(self, key, item):
		item = self.init(item, logs=True)
		self._log_call(method=self.__setitem__, key=key, item=item)
		super(Edict, self).__setitem__(key=key, v=item)

	def __delitem__(self, key):
		self._log_call(method=self.__delitem__, key=key)
		super(Edict, self).__delitem__(key=key)

	def clear(self):
		self._log_call(method=self.clear)
		self._p_log = False
		super(Edict, self).clear()
		self._p_log = True


class Elist(Elog, PersistentList):

	@staticmethod
	def field(data: list = [], logs: bool = True):
		return field(default_factory=lambda: Elist(data=data, logs=logs))

	def __init__(self, data: list[any] = None, logs: bool = True):
		data = self.init(data=data, logs=logs)
		super(Elist, self).__init__(initlist=data)
		if logs:
			self._logs = Elist(logs=False)
			self.log_call(method=self.__init__, type=LogType.ELIST_INIT, args=data)

	def __setitem__(self, i, item):
		self._log_call(method=self.__setitem__, i=i, item=item)
		super(Elist, self).__setitem__(i=i, item=item)

	def __add__(self, other: any):
		elist = super(Elist, self).__add__(other=other)
		elist._logs = self._logs
		elist._log_call(method=self.__add__, other=other)
		return elist

	def __radd__(self, other):
		elist = super(Elist, self).__radd__(other=other)
		elist._logs = self._logs
		elist._log_call(method=self.__radd__, other=other)
		return elist

	def __iadd__(self, other):
		elist = super(Elist, self).__iadd__(other=other)
		elist._logs = self._logs
		elist._log_call(method=self.__iadd__, other=other)
		return elist

	def __mul__(self, n):
		elist = super(Elist, self).__mul__(n=n)
		elist._logs = self._logs
		elist._log_call(method=self.__mul__, n=n)
		return elist

	def __rmul__(self, n):
		elist = super(Elist, self).__rmul__(n=n)
		elist._logs = self._logs
		elist._log_call(method=self.__rmul__, n=n)
		return elist

	def __imul__(self, n):
		elist = super(Elist, self).__imul__(n=n)
		elist._logs = self._logs
		elist._log_call(method=self.__imul__, n=n)
		return elist

	def __contains__(self, item):
		for ele in self:
			if isinstance(ele, Entity):
				if ele.equal(item):
					return True
			elif ele == item:
				return True
		return False

	def append(self, item: object):
		self._log_call(method=self.append, item=item)
		if cutils.is_object(item):
			for k, v in item.__dict__.items():
				if isinstance(v, list | tuple):
					setattr(item, k, PersistentList(v))
		super(Elist, self).append(item)

	def clear(self):
		self._log_call(method=self.clear)
		super(Elist, self).clear()

	def insert(self, i, item):
		self._log_call(method=self.insert, i=i, item=item)
		super(Elist, self).insert(i, item)

	def pop(self, i=-1):
		self._log_call(method=self.pop, i=i)
		return super(Elist, self).pop(i)

	def remove(self, item):
		self._log_call(method=self.remove, item=item)
		super(Elist, self).remove(item=item)

	def reverse(self):
		self._log_call(method=self.reverse)
		super(Elist, self).reverse()

	def sort(self, reverse: bool = False, key: Callable = None):
		self._log_call(method=self.sort, reverse=reverse, key=key)
		super(Elist, self).sort(reverse=reverse, key=key)

	def extend(self, other):
		self._log_call(method=self.extend, other=other)
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


T = TypeVar('T')
elist = list[T] | Elist
edict = list[T] | Edict


class Entity(Elog, Persistent):  # TODO: Try to add EPersists and refactor __post_init__ to EPersists
	_id: str | None
	_type: str | None
	_created: datetime | None
	_updated: datetime | None
	_logs: elist | None
	_connections: elist | None

	def __post_init__(self):
		# * SETUP ADDITIONAL PROPERTIES FOR EVERY ENTITIES!
		self._id = shortuuid.uuid()
		self._type = self.__class__.__name__.lower()
		self._created = datetime.now()
		self._updated = datetime.now()
		self._connections = Elist(logs=not isinstance(self, Log))
		self._logs = Elist(logs=False)

		# ! GO ONLY ONE LAYER DEEP!!!!!!!!
		# * CONVERT PROPERTIES OF (LIST, TUPLES, DICT) TO SAFE VARIANTS (Elist, Edict)
		for k, v in self.__dict__.items():
			if isinstance(v, list | tuple | set):
				self.__dict__[k] = Elist(data=v)
			elif isinstance(v, dict):
				self.__dict__[k] = Edict(data=v)

		# * CLEAN LOGS THAT HAS BEEN POLUTED BY __INIT__ METHOD.
		for k, v in self.__dict__.items():
			if hasattr(v, '_logs'):
				self.__dict__[k]._logs.clear()

		# * LOG __INIT__ METHOD FOR ENTITY
		if not isinstance(self, Log):
			kwargs = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
			self.log_call(method=self.__init__, type=LogType.ENTITY_INIT, **kwargs)

	def __setattr__(self, key, value):
		# * IF LOGGING IS ACTIVATED, HAS DIARY INSIDE, IS NOT ZOODB PROPERTY, DO NOT LOG SETTING _logging FLAG
		if self.is_logging and not key.startswith('_p_'):
			value_str = f"'{value}'" if isinstance(value, str) else str(value)
			log_obj = Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg=f'{key} = {value_str}')
			self._logs.append(log_obj)
		super(Entity, self).__setattr__(key, value)

	def __delattr__(self, item):
		raise Exception("Not allowed!")

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
	type: LogType
	msg: str
	data: Edict = Edict.field(logs=False)  # Todo: test if changes in data propagate to db elements.
