import logging
import unittest


class test_logger(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.log = logging.getLogger(__name__)

	def test_values(self):
		with self.assertLogs(__name__, level='INFO') as cm:
			self.log.info('first message')
			self.log.error('second message')
			self.assertEqual(cm.output[0].split(':')[::2], ['INFO', 'first message'])
			self.assertEqual(cm.output[1].split(':')[::2], ['ERROR', 'second message'])


if __name__ == '__main__':
	unittest.main()
