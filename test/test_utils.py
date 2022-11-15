import unittest
from datetime import datetime
from pathlib import Path

from core import utils
from test import helpers


class test_validate(unittest.TestCase):

	def test_root_path(self):
		result = utils.root_path('api')
		self.assertEqual(result, (Path(__file__).parent.joinpath('../api').resolve().absolute()))

	def test_age(self):
		today = datetime.utcnow()
		self.assertEqual(12.5027, round(utils.age(today.year - 12, today.month - 6, today.day - 1), 4))

	def test_is_iterable(self):
		for ele in helpers.iterables:
			self.assertTrue(utils.is_iterable(ele), ele)

		for ele in helpers.dicts + helpers.values + helpers.objects:
			self.assertFalse(utils.is_iterable(ele), ele)

	def test_is_mappable(self):
		for ele in helpers.dicts:
			self.assertTrue(utils.is_mappable(ele), ele)

		for ele in helpers.iterables + helpers.values + helpers.objects:
			self.assertFalse(utils.is_mappable(ele), ele)

	def test_is_object(self):
		for ele in helpers.objects:
			self.assertTrue(utils.is_object(ele), ele)

		for ele in helpers.dicts + helpers.iterables + helpers.values:
			self.assertFalse(utils.is_object(ele), ele)

	def test_object_path(self):
		self.assertEqual(helpers.tree, utils.object_path(helpers.tree, '/'))
		self.assertEqual(helpers.tree, utils.object_path(helpers.tree))
		self.assertEqual(helpers.tree, utils.object_path(helpers.tree, ''))

		def test(obj, path):
			self.assertEqual(obj, utils.object_path(helpers.tree, path))
			if isinstance(obj, list):
				return True
			self.assertEqual(obj.j, utils.object_path(helpers.tree, f'{path}/j'))
			self.assertEqual(obj.f[3], utils.object_path(helpers.tree, f'{path}/f/3'))
			self.assertEqual(obj.g['d'], utils.object_path(helpers.tree, f'{path}/g/d'))
			self.assertEqual(obj.j[-1], utils.object_path(helpers.tree, f'{path}/j/-1'))
			self.assertEqual(obj.k, utils.object_path(helpers.tree, f'{path}/k'))
			self.assertEqual(obj.l, utils.object_path(helpers.tree, f'{path}/l'))
			self.assertEqual(obj.n, utils.object_path(helpers.tree, f'{path}/n'))
			self.assertEqual(obj.o, utils.object_path(helpers.tree, f'{path}/o'))
			return True

		self.assertTrue(test(helpers.tree, ''))
		self.assertTrue(test(helpers.tree.o, '/o'))
		self.assertTrue(test(helpers.tree.o[0], '/o/0/'))
		self.assertTrue(test(helpers.tree.o[0].o, '/o/0/o'))

	def test_object_json(self):
		self.assertEqual(utils.object_json([helpers.tree, helpers.tree], max_depth=10), [helpers.tree_json, helpers.tree_json])

	def test_object_json_max_depth_width(self):
		self.assertEqual(utils.object_json(helpers.tree2, max_width=2, max_depth=0), 'MAX_DEPTH_LIST')
		self.assertEqual(utils.object_json(helpers.tree2, max_width=2, max_depth=1), ['MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT', 'MAX_WIDTH'])
		self.assertEqual(utils.object_json(helpers.tree2, max_width=1, max_depth=2), [
			{'child': 'MAX_DEPTH_LIST', 'data': 1},
			'MAX_WIDTH'
		])
		self.assertEqual(utils.object_json(helpers.tree2, max_width=3, max_depth=3), [
			{'child': ['MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT', 'MAX_DEPTH_OBJECT'], 'data': 1},
			{'child': [], 'data': 2},
			{'child': [], 'data': 3},
			'MAX_WIDTH'
		])
		self.assertEqual(utils.object_json(helpers.tree2, max_width=4, max_depth=4), [
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
		self.assertEqual(utils.object_json(helpers.tree2, max_width=10, max_depth=5), [
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

	def test_filter_dict(self):
		def test(a, b, c, d):
			raise Exception()

		kwargs = {
			'a': 'a',
			'b': 'b',
			'c': 'c',
			'd': 'd',
			'e': 'e',
			'f': 'f',
		}

		self.assertEqual({
			'a': 'a',
			'b': 'b',
			'c': 'c',
			'd': 'd',
		}, utils.filter_dict(test, kwargs))

if __name__ == '__main__':
	unittest.main()
