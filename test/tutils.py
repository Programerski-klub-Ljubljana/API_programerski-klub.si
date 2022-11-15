from persistent.list import PersistentList


class Node:
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


class Node2:
	def __init__(self, v, child):
		self.data = v
		self.child = child
		self._dnevnik = '_dnevnik'


dicts = [{'key': 1, 'key2': 'asdf'}, {}]
iterables = [[1, "asdf", True], (1, "asdf", True), {1, 2, 3}, PersistentList()]
values = [None, True, 1, 1.2, "asdf"]
objects = [Node(c=[])]

tree = Node(c=[Node(c=Node(c=[]))])
tree_json = {
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

tree2 = [
	Node2(1, child=[
		Node2(11, child=[
			Node2(21, child=[
				Node2(31, child=[]),
				Node2(32, child=[]),
				Node2(33, child=[]),
				Node2(34, child=[]),
			]),
			Node2(22, child=[]),
			Node2(23, child=[]),
			Node2(24, child=[]),
		]),
		Node2(12, child=[]),
		Node2(13, child=[]),
		Node2(14, child=[]),
	]),
	Node2(2, child=[]),
	Node2(3, child=[]),
	Node2(4, child=[]),
]
