from enum import Enum, auto


class EntityEnum(str, Enum):
	def _generate_next_value_(self, start, count, last_values):
		return self

	@classmethod
	def values(cls) -> list[str]:
		return list(map(lambda c: c.value, cls))


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
