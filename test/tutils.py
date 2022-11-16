import sys

from persistent.list import PersistentList
from starlette.testclient import TestClient

this = sys.modules[__name__]
client: TestClient | None = None


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


class Fixtures:
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
