from dataclasses import dataclass
from unittest.mock import MagicMock

from persistent.list import PersistentList

from core.domain._entity import Entity, elist, edict, Edict, Elist


class AsyncMock(MagicMock):
	async def __call__(self, *args, **kwargs):
		return super(AsyncMock, self).__call__(*args, **kwargs)

	def __enter__(self):
		return self


class BigNode:
	def __init__(self, c):
		# 15
		self.a = None
		self.b = True
		self.c = 1
		self.d = 1.2
		self.e = "abc"
		self.f = [None, True, 1, 1.2, "asdf", [1, 2, 3], {'a': 1, 'b': 2}]
		self.g = {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}}
		self.j = PersistentList([1, 2, 3])
		self.k = []
		self.l = {}
		self.n = PersistentList()
		self.o = c


class SmallNode:
	def __init__(self, v, child):
		self.data = v
		self.child = child
		self._dnevnik = '_dnevnik'


class Cutils_fixtures:
	dicts = [{'key': 1, 'key2': 'asdf'}, {}]
	iterables = [[1, "asdf", True], (1, "asdf", True), {1, 2, 3}, PersistentList()]
	values = [None, True, 1, 1.2, "asdf"]
	objects = [BigNode(c=[])]
	tree_wide = BigNode(c=[BigNode(c=BigNode(c=[]))])
	tree_wide_json = {
		'a': None,
		'b': True,
		'c': 1,
		'd': 1.2,
		'e': 'abc',
		'f': [None, True, 1, 1.2, 'asdf', [1, 2, 3], {'a': 1, 'b': 2}],
		'g': {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}},
		'j': [1, 2, 3],
		'k': [],
		'l': {},
		'n': [],
		'o': [
			{
				'a': None,
				'b': True,
				'c': 1,
				'd': 1.2,
				'e': 'abc',
				'f': [None, True, 1, 1.2, 'asdf', [1, 2, 3], {'a': 1, 'b': 2}],
				'g': {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}},
				'j': [1, 2, 3],
				'k': [],
				'l': {},
				'n': [],
				'o': {
					'a': None,
					'b': True,
					'c': 1,
					'd': 1.2,
					'e': 'abc',
					'f': [None, True, 1, 1.2, 'asdf', [1, 2, 3], {'a': 1, 'b': 2}],
					'g': {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}},
					'j': [1, 2, 3],
					'k': [],
					'l': {},
					'n': [],
					'o': [],
				}
			}]
	}
	tree_deep = [
		SmallNode(1, child=[
			SmallNode(11, child=[
				SmallNode(21, child=[
					SmallNode(31, child=[]),
					SmallNode(32, child=[]),
					SmallNode(33, child=[]),
					SmallNode(34, child=[]),
				]),
				SmallNode(22, child=[]),
				SmallNode(23, child=[]),
				SmallNode(24, child=[]),
			]),
			SmallNode(12, child=[]),
			SmallNode(13, child=[]),
			SmallNode(14, child=[]),
		]),
		SmallNode(2, child=[]),
		SmallNode(3, child=[]),
		SmallNode(4, child=[]),
	]


class Entity_fixtures:
	@staticmethod
	def entity(cls, level=0):
		if level >= 0:
			return cls(
				a=True, b=32, c=.23, d="asd",
				e=Entity_fixtures.entity(cls, level - 1),
				f=Entity_fixtures.list(cls, level - 1),
				g=Entity_fixtures.dict(cls, level - 1),
				h=Entity_fixtures.tuple(cls, level - 1)
			)

	@staticmethod
	def list(cls, level=0) -> list:
		if level >= 0:
			return [
				3.21, False, 321, "mata",
				Entity_fixtures.entity(cls, level - 1),
				Entity_fixtures.list(cls, level - 1),
				Entity_fixtures.dict(cls, level - 1),
				Entity_fixtures.tuple(cls, level - 1)
			]

	@staticmethod
	def tuple(cls, level=0) -> list:
		if level >= 0:
			return (
				3.21, False, 321, "mata",
				Entity_fixtures.entity(cls, level - 1),
				Entity_fixtures.list(cls, level - 1),
				Entity_fixtures.dict(cls, level - 1),
				Entity_fixtures.tuple(cls, level - 1)
			)

	@staticmethod
	def dict(cls, level=0) -> dict:
		if level >= 0:
			return {
				'a': True, 'b': 123, 'c': 1.23, 'd': "data",
				'e': Entity_fixtures.entity(cls, level - 1),
				'f': Entity_fixtures.list(cls, level - 1),
				'g': Entity_fixtures.dict(cls, level - 1),
				'h': Entity_fixtures.tuple(cls, level - 1)
			}


@dataclass
class EntitySmall(Entity):
	a: bool
	b: int
	c: float
	d: str
	e: 'EntityBig | EntitySmall | None'
	f: elist
	g: edict
	h: elist


@dataclass
class EntityBig(Entity):
	a: bool
	b: int
	c: float
	d: str
	e: 'EntityBig'
	f: elist
	g: edict
	h: elist
	j: 'EntityBig' = Entity_fixtures.entity(EntitySmall, 2)
	k: elist = Elist.field(data=Entity_fixtures.list(EntitySmall, 2))
	l: edict = Edict.field(data=Entity_fixtures.dict(EntitySmall, 2))
