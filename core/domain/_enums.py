import random
from enum import Enum, auto
from functools import total_ordering


@total_ordering
class EntityEnum(str, Enum):
	@classmethod
	def values(cls) -> list[str]:
		return list(cls)

	@classmethod
	def random(cls):
		return random.choice(cls.values())

	def equal(self, ele):
		return self == ele

	@staticmethod
	def _generate_next_value_(name: str, start: int, count: int, last_values: list) -> str:
		return name

	def __str__(self):
		return str(self.value)

	def __repr__(self):
		return str(self.value)


class LogLevel(EntityEnum):
	DEBUG = auto()
	INFO = auto()
	WARNING = auto()
	ERROR = auto()


class LogType(EntityEnum):
	ENTITY = auto()
	ELIST = auto()
	EDICT = auto()

	ENTITY_INIT = auto()
	ELIST_INIT = auto()
	EDICT_INIT = auto()
