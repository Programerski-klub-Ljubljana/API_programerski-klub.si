from abc import ABC, abstractmethod


class DbService(ABC):
	@abstractmethod
	def path(self, entity: str, path: str | None = None):
		pass

	@abstractmethod
	def save(self, *entities):
		pass

	@abstractmethod
	def transaction(self, note: str | None = None):
		pass

	@abstractmethod
	def seed(self):
		pass
