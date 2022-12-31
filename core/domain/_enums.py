import random
from enum import Enum
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
	DEBUG = "DEBUG"
	INFO = "INFO"
	WARNING = "WARNING"
	ERROR = "ERROR"


class LogType(EntityEnum):
	ENTITY = "ENTITY"
	ELIST = "ELIST"
