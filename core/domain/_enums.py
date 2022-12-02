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

	def __lt__(self, other):
		if self.__class__ is other.__class__:
			return self.value < other.value
		raise Exception("Not implemented")


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
