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
	# * STRICT PRIVATE (DO NOT LOGS THIS)
	_p_log: bool
	_p_logs: PersistentList
	_p_updated: datetime
	_p_created: datetime

	def __post_init__(self, *args, **kwargs):
		# * SETUP ADDITIONAL PROPERTIES FOR EVERY ENTITIES!
		self._p_log = False
		self._p_logs = PersistentList()
		self._p_created = datetime.now()
		self._p_updated = datetime.now()
		self._p_log = True

		type = getattr(LogType, f'{self.log_type}_INIT')
		self.log_call(method=self.__init__, type=type, args=args, **kwargs)

	@staticmethod
	def init(data: any, wrap: bool):
		if isinstance(data, list | tuple | set):
			data = list(data)
			iterator = enumerate(data)
			wraper = Elist
		elif isinstance(data, dict):
			iterator = data.items()
			wraper = Edict
		else:
			return data

		for k, v in iterator:
			if isinstance(v, list | tuple | set):
				data[k] = Elist(data=list(v))
			elif isinstance(v, dict):
				data[k] = Edict(data=v)

		return wraper(data=data) if wrap else data

	@property
	def logs(self):
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
				iterator = self.__dict__.items()
				key_formator = lambda key: f'{key}'

		logs = deepcopy(self._p_logs)
		for k, v in iterator:
			if isinstance(v, Elog):
				for l in deepcopy(v._p_logs):  # ! ORIGINALNIH LOGOV SE NE SME SPREMINJATI!
					if l.type not in [LogType.EDICT_INIT, LogType.ELIST_INIT, LogType.ENTITY_INIT]:  # ! IGNORE INIT LOGS IN SECOND LEVEL.
						l.msg = f'{key_formator(k)}.{l.msg}'
						logs.append(l)
		return sorted(logs, key=lambda l: l.created)

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

	def log(self, level: LogLevel, type: LogType, msg: str, args=(), **kwargs):
		if hasattr(self, '_p_updated'):
			self._p_updated = datetime.now()  # * IF LOGS THEN IT WAS UPDATED
		if getattr(self, '_p_log', False):
			log_obj = Log(level=level, type=type, msg=msg, args=args, kwargs=kwargs)  # * DEEP COPY SE NAREDI V LOGSU
			self._p_logs.append(log_obj)

	def _log_call(self, method: Callable, args=(), **kwargs):
		self.log_call(method=method, type=self.log_type, args=args, **kwargs)

	def log_call(self, method: Callable, type: LogType, args=(), **kwargs):
		args_str = cutils.args_str(*args) if len(args) > 0 else ''
		join_str = ', ' if len(args) * len(kwargs) > 0 else ''
		self.log(
			level=LogLevel.DEBUG, type=type,
			msg=f'{method.__name__}({args_str}{join_str}{cutils.kwargs_str(**kwargs)})',
			args=args, **kwargs)

	def log_debug(self, type: LogType, msg: str, args=(), **kwargs):
		self.log(level=LogLevel.DEBUG, type=type, msg=msg, args=args, **kwargs)

	def log_info(self, type: LogType, msg: str, args=(), **kwargs):
		self.log(level=LogLevel.INFO, type=type, msg=msg, args=args, **kwargs)

	def log_warning(self, type: LogType, msg: str, args=(), **kwargs):
		self.log(level=LogLevel.WARNING, type=type, msg=msg, args=args, **kwargs)

	def log_error(self, type: LogType, msg: str, args=(), **kwargs):
		self.log(level=LogLevel.ERROR, type=type, msg=msg, args=args, **kwargs)


class Edict(Elog, PersistentMapping):

	def __init__(self, data: dict = None):
		if data is None:
			data = {}
		super(Edict, self).__post_init__(**data)
		data = self.init(data=data, wrap=False)

		self._p_log = False
		super(Edict, self).__init__(data)
		self._p_log = True

	@staticmethod
	def field(data: dict = None):
		if data is None:
			data = {}
		return field(default_factory=lambda: Edict(data=data))

	def __setitem__(self, key, item):
		self._log_call(method=self.__setitem__, key=key, item=item)
		item = self.init(data=item, wrap=True)
		super(Edict, self).__setitem__(key=key, v=item)

	def __delitem__(self, key):
		self._log_call(method=self.__delitem__, key=key)
		super(Edict, self).__delitem__(key=key)

	def clear(self):
		# ! DO NOT LOGS EVERY SINGLE __DELITEM__ THAT HAPPEND IN CLEAR METHOD
		self._log_call(method=self.clear)
		self._p_log = False
		super(Edict, self).clear()
		self._p_log = True


class Elist(Elog, PersistentList):

	def __init__(self, data: list[any] = ()):
		super(Elist, self).__post_init__(*data)
		data = self.init(data=data, wrap=False)

		self._p_log = False
		super(Elist, self).__init__(initlist=data)
		self._p_log = True

	@staticmethod
	def field(data: list = ()):
		return field(default_factory=lambda: Elist(data=data))

	def __setitem__(self, i, item):
		self._log_call(method=self.__setitem__, i=i, item=item)
		item = self.init(data=item, wrap=True)
		super(Elist, self).__setitem__(i=i, item=item)

	def __add__(self, other: list):
		self._log_call(method=self.__add__, other=other)
		elist = super(Elist, self).__add__(other=other)
		elist._p_logs = self._p_logs
		return elist

	def __radd__(self, other: list):
		elist = super(Elist, self).__radd__(other=other)
		elist._p_logs = self._p_logs
		elist._log_call(method=self.__radd__, other=other)
		return elist

	def __iadd__(self, other: list):
		other = self.init(data=other, wrap=False)
		elist = super(Elist, self).__iadd__(other=other)
		elist._logs = self._p_logs
		elist._log_call(method=self.__iadd__, other=other)
		return elist

	def __mul__(self, n):
		elist = super(Elist, self).__mul__(n=n)
		elist._p_logs = self._p_logs
		elist._log_call(method=self.__mul__, n=n)
		return elist

	def __rmul__(self, n):
		elist = super(Elist, self).__rmul__(n=n)
		elist._p_logs = self._p_logs
		elist._log_call(method=self.__rmul__, n=n)
		return elist

	def __imul__(self, n):
		elist = super(Elist, self).__imul__(n=n)
		elist._logs = self._p_logs
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
		item = self.init(data=item, wrap=True)
		super(Elist, self).append(item)

	def clear(self):
		self._log_call(method=self.clear)
		super(Elist, self).clear()

	def insert(self, i, item):
		self._log_call(method=self.insert, i=i, item=item)
		item = self.init(data=item, wrap=True)
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
		key_src = cutils.lambda_src(key)
		self._log_call(method=self.sort, reverse=reverse, key=key_src)
		super(Elist, self).sort(reverse=reverse, key=key)

	def extend(self, other: list):
		self._log_call(method=self.extend, other=other)
		other = self.init(data=other, wrap=True)
		super(Elist, self).extend(other)

	def random(self, k: int = None):
		return choice(self) if k is None else choices(self, k=k)

	def path(self, path: str = None, page: int = 0, max_width: int = 10) -> any:
		result = cutils.object_path(self, path)
		start = max_width * page
		end = max_width * (page + 1)
		return result[start:end] if cutils.is_iterable(result) else result


T = TypeVar('T')
elist = list[T] | Elist
edict = list[T] | Edict


class Entity(Elog, Persistent):  # TODO: Try to add EPersists and refactor __post_init__ to EPersists
	# * WEAK PRIVATE (SHOULD LOG)
	_id: str = None
	_type: str = None
	_connections: Elist = None

	def __post_init__(self):
		super(Entity, self).__post_init__(**self.__dict__)

		self._p_log = False
		self._id = shortuuid.uuid()
		self._type = self.__class__.__name__.lower()
		self._connections = Elist()
		self._p_log = True

		self.init(data=self.__dict__, wrap=False)  # * CONVERT INNER STRUCTURES TO SAFE VARIANTS!

	def __setattr__(self, key, value):
		if not key.startswith('_p_'):
			self._log_call(method=self.__setattr__, key=key, value=value)
		value = self.init(data=value, wrap=True)
		super(Entity, self).__setattr__(key, value)

	def equal(self, entity):
		return self == entity

	def connect(self, *entity):
		for e in entity:
			if e not in self._connections:
				self._connections.append(e)
			if self not in e._connections:
				e._connections.append(self)


# ! THIS SHALL BE INDEPENDENT ELEMENT FOR SIMPLICITY SAKE!
@dataclass
class Log(Persistent):
	level: LogLevel
	type: LogType
	msg: str

	# ! It will never happend that you want to change logs.data
	created: datetime = None
	args: tuple = None
	kwargs: dict = None

	def __post_init__(self):
		self.created = datetime.now()
		self.args = tuple(deepcopy(self.args))
		self.kwargs = deepcopy(self.kwargs)
