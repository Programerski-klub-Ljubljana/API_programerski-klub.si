from abc import ABC, abstractmethod


class DbService(ABC):
	@abstractmethod
	def save_clan(self, clan):
		pass
