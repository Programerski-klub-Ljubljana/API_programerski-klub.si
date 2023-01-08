import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

from core import cutils
from core.domain._entity import Entity, Elist, Edict
from test.tutils import Cutils_fixtures, EntitySmall


class test_cutils(unittest.TestCase):

	def test_root_path(self):
		result = cutils.root_path('api')
		test = Path(__file__).absolute().parent.parent.parent.joinpath('api')
		self.assertEqual(result, test)

	def test_age(self):
		today = datetime.now()
		self.assertEqual(12.0, round(cutils.age(today.year - 12, today.month, today.day), 2))
		self.assertEqual(-12.0, round(cutils.age(today.year + 12, today.month, today.day), 2))

	def test_is_iterable(self):
		self.assertFalse(cutils.is_iterable(1))
		self.assertFalse(cutils.is_iterable(1.3))
		self.assertFalse(cutils.is_iterable(True))
		self.assertFalse(cutils.is_iterable('asdf'))
		self.assertTrue(cutils.is_iterable([1, 2, 3]))
		self.assertTrue(cutils.is_iterable((1, 2, 3)))
		self.assertTrue(cutils.is_iterable({1, 2, 3}))
		self.assertFalse(cutils.is_iterable({'a': 1}))
		self.assertTrue(cutils.is_iterable(PersistentList([1, 2, 3])))
		self.assertFalse(cutils.is_iterable(PersistentMapping({'a': 1})))
		self.assertTrue(cutils.is_iterable(Elist()))
		self.assertFalse(cutils.is_iterable(Edict()))
		self.assertFalse(cutils.is_iterable(Entity()))

	def test_is_mappable(self):
		self.assertFalse(cutils.is_mappable(1))
		self.assertFalse(cutils.is_mappable(1.3))
		self.assertFalse(cutils.is_mappable(True))
		self.assertFalse(cutils.is_mappable('asdf'))
		self.assertFalse(cutils.is_mappable([1, 2, 3]))
		self.assertFalse(cutils.is_mappable((1, 2, 3)))
		self.assertFalse(cutils.is_mappable({1, 2, 3}))
		self.assertTrue(cutils.is_mappable({'a': 1}))
		self.assertFalse(cutils.is_mappable(PersistentList([1, 2, 3])))
		self.assertTrue(cutils.is_mappable(PersistentMapping({'a': 1})))
		self.assertFalse(cutils.is_mappable(Elist()))
		self.assertTrue(cutils.is_mappable(Edict()))
		self.assertFalse(cutils.is_mappable(Entity()))
		self.assertFalse(cutils.is_mappable(EntitySmall(False, 1, 2.3, "asdf", None, None, None, None)))

	def test_is_object(self):
		self.assertFalse(cutils.is_object(1))
		self.assertFalse(cutils.is_object(1.3))
		self.assertFalse(cutils.is_object(True))
		self.assertFalse(cutils.is_object('asdf'))
		self.assertFalse(cutils.is_object([1, 2, 3]))
		self.assertFalse(cutils.is_object((1, 2, 3)))
		self.assertFalse(cutils.is_object({1, 2, 3}))
		self.assertFalse(cutils.is_object({'a': 1}))
		self.assertFalse(cutils.is_object(PersistentList([1, 2, 3])))
		self.assertFalse(cutils.is_object(PersistentMapping({'a': 1})))
		self.assertFalse(cutils.is_object(Elist()))
		self.assertFalse(cutils.is_object(Edict()))
		self.assertTrue(cutils.is_object(Entity()))
		self.assertTrue(cutils.is_object(EntitySmall(False, 1, 2.3, "asdf", None, None, None, None)))

	def test_object_path(self):
		self.assertEqual(Cutils_fixtures.tree_wide, cutils.object_path(Cutils_fixtures.tree_wide, '/'))
		self.assertEqual(Cutils_fixtures.tree_wide, cutils.object_path(Cutils_fixtures.tree_wide))
		self.assertEqual(Cutils_fixtures.tree_wide, cutils.object_path(Cutils_fixtures.tree_wide, ''))

		def test(obj, path):
			self.assertEqual(obj, cutils.object_path(Cutils_fixtures.tree_wide, path))
			if isinstance(obj, list):
				return True
			self.assertEqual(obj.j, cutils.object_path(Cutils_fixtures.tree_wide, f'{path}/j'))
			self.assertEqual(obj.f[3], cutils.object_path(Cutils_fixtures.tree_wide, f'{path}/f/3'))
			self.assertEqual(obj.g['d'], cutils.object_path(Cutils_fixtures.tree_wide, f'{path}/g/d'))
			self.assertEqual(obj.j[-1], cutils.object_path(Cutils_fixtures.tree_wide, f'{path}/j/-1'))
			self.assertEqual(obj.k, cutils.object_path(Cutils_fixtures.tree_wide, f'{path}/k'))
			self.assertEqual(obj.l, cutils.object_path(Cutils_fixtures.tree_wide, f'{path}/l'))
			self.assertEqual(obj.n, cutils.object_path(Cutils_fixtures.tree_wide, f'{path}/n'))
			self.assertEqual(obj.o, cutils.object_path(Cutils_fixtures.tree_wide, f'{path}/o'))
			return True

		self.assertTrue(test(Cutils_fixtures.tree_wide, ''))
		self.assertTrue(test(Cutils_fixtures.tree_wide.o, '/o'))
		self.assertTrue(test(Cutils_fixtures.tree_wide.o[0], '/o/0/'))
		self.assertTrue(test(Cutils_fixtures.tree_wide.o[0].o, '/o/0/o'))

	def test_object_json(self):
		self.assertEqual(cutils.object_json([Cutils_fixtures.tree_wide, Cutils_fixtures.tree_wide], max_depth=10),
		                 [Cutils_fixtures.tree_wide_json, Cutils_fixtures.tree_wide_json])

	def test_object_json_max_depth_width(self):
		self.assertEqual(cutils.object_json(Cutils_fixtures.tree_deep, max_width=2, max_depth=0), 'MAX_DEPTH_LIST')
		self.assertEqual(
			cutils.object_json(Cutils_fixtures.tree_deep, max_width=2, max_depth=1),
			['MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT', 'MAX_WIDTH'])
		self.assertEqual(cutils.object_json(Cutils_fixtures.tree_deep, max_width=1, max_depth=2), [
			{'child': 'MAX_DEPTH_LIST', 'data': 1},
			'MAX_WIDTH'
		])
		self.assertEqual(cutils.object_json(Cutils_fixtures.tree_deep, max_width=3, max_depth=3), [
			{'child': ['MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT', 'MAX_WIDTH'], 'data': 1},
			{'child': [], 'data': 2},
			{'child': [], 'data': 3},
			'MAX_WIDTH'
		])
		self.assertEqual(cutils.object_json(Cutils_fixtures.tree_deep, max_width=4, max_depth=4), [
			{
				'child': [
					{'child': 'MAX_DEPTH_LIST', 'data': 11},
					{'child': 'MAX_DEPTH_LIST', 'data': 12},
					{'child': 'MAX_DEPTH_LIST', 'data': 13},
					{'child': 'MAX_DEPTH_LIST', 'data': 14}
				],
				'data': 1
			},
			{'child': [], 'data': 2},
			{'child': [], 'data': 3},
			{'child': [], 'data': 4}
		])
		self.assertEqual(cutils.object_json(Cutils_fixtures.tree_deep, max_width=10, max_depth=5), [
			{
				'child': [
					{
						'child': ['MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT'],
						'data': 11
					},
					{'child': [], 'data': 12},
					{'child': [], 'data': 13},
					{'child': [], 'data': 14}
				],
				'data': 1
			},
			{'child': [], 'data': 2},
			{'child': [], 'data': 3},
			{'child': [], 'data': 4}
		])

	def test_call(self):
		def test(a, b, c, d):
			return a + b + c + d

		kwargs = {
			'a': 'a',
			'b': 'b',
			'c': 'c',
			'd': 'd',
			'e': 'e',
			'f': 'f',
		}

		self.assertEqual("abcd", cutils.call(test, **kwargs))

	def test_list_field(self):
		@dataclass
		class FakeDataclass:
			test: list = cutils.list_field(1, 2, 3)

		dc = FakeDataclass()
		self.assertCountEqual(dc.test, [1, 2, 3])

	def test_lambda_src(self):
		self.assertEqual("lambda x: x.test", cutils.lambda_src(lambda x: x.test))
		self.assertEqual("lambda x, y: x.arg0 + y.arg1", cutils.lambda_src(lambda x, y: x.arg0 + y.arg1))
		self.assertEqual("lambda: True", cutils.lambda_src(lambda: True))

	def test_kwargs_str(self):
		self.assertEqual(
			"arg0='arg0', arg1='arg1', arg2=[1, True, 2.3, 'str'], arg3={'a': 1, 'c': 'd', 'e': 2.3}, arg4=lambda x: x.arg1",
			cutils.kwargs_str(
				self=123, arg0='arg0', arg1='arg1',
				arg2=[1, True, 2.3, "str"],
				arg3={'a': 1, 'c': 'd', 'e': 2.3},
				arg4=lambda x: x.arg1
			))


if __name__ == '__main__':
	unittest.main()
