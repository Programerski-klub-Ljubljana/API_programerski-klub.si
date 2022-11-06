from contextlib import contextmanager
from random import randint, choices
from typing import Iterator, Union

import ZODB.FileStorage
from faker import Faker
from faker.providers import address, company, date_time, internet, person, phone_number, ssn
from persistent.list import PersistentList

from src.domain.arhitektura_kluba import Clan, Ekipa, Oddelek, Klub

db = ZODB.DB(None)


class Root:
	def __init__(self, root):
		self.klubi: PersistentList | list[Klub] = root.klubi
		self.clani: PersistentList | list[Clan] = root.clani
		self.ekipe: PersistentList | list[Ekipa] = root.ekipe
		self.oddelki: PersistentList | list[Oddelek] = root.oddelki


@contextmanager
def transaction(note: str = None) -> Iterator[Root]:
	with db.transaction(note=note) as con:
		yield Root(con.root)


fake: Union[
	address.Provider,
	company.Provider,
	date_time.Provider,
	internet.Provider,
	person.Provider,
	phone_number.Provider,
	ssn.Provider,
	Faker] = Faker("sl_SI")


def seed(root: Root, clani: int, ekipe: int, oddeleki: int, klubi: int):
	root.clani = PersistentList()
	for i in range(clani):
		root.clani.append(Clan(
			ime=fake.first_name(),
			priimek=fake.last_name(),
			rojen=fake.date_this_century(before_today=True),
			email=fake.email(),
			telefon=[fake.phone_number() for i in range(randint(1, 3))],
			vpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))],
			izpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))]
		))

	root.ekipe = PersistentList()
	for i in range(ekipe):
		root.ekipe.append(Ekipa(
			ime=fake.company(),
			opis=fake.catch_phrase()
		))

	root.oddelki = PersistentList()
	for i in range(oddeleki):
		root.oddelki.append(Oddelek(
			ime=fake.company(),
			opis=fake.catch_phrase(),
			ekipe=choices(root.ekipe, k=randint(1, 10))
		))

	root.klubi = PersistentList()
	for i in range(klubi):
		root.klubi.append(Klub(
			oddelki=root.oddelki
		))


def init():
	with db.transaction(note="seed.migrate") as con:
		seed(con.root, clani=60, ekipe=20, oddeleki=6, klubi=2)


init()
with transaction() as root:
	print(root.klubi)
	print(root.oddelki)
