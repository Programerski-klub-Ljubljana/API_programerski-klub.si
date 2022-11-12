import random
from enum import Enum, auto


class EntityEnum(str, Enum):
	@classmethod
	def values(cls) -> list[str]:
		return list(map(lambda c: c.value, cls))

	@classmethod
	def random(cls):
		return random.choice(cls.values())


class LogLevel(EntityEnum):
	DEBUG = auto()
	INFO = auto()
	WARNING = auto()
	ERROR = auto()


class LogTheme(EntityEnum):
	OSNOVNOSOLSKI = auto()
	SREDNJESOLSKI = auto()
	GITHUB = auto()
	PREKRSEK = auto()
	PROBLEM = auto()
