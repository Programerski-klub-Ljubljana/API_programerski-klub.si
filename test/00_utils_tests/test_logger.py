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
			self.assertEqual(cm.output, ['INFO:test_logger:first message',
			                             'ERROR:test_logger:second message'])


if __name__ == '__main__':
	unittest.main()
