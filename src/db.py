from contextlib import contextmanager
from random import randint, choices, choice, uniform
from typing import Iterator, Union

import ZODB.FileStorage
from faker import Faker
from faker.providers import address, company, date_time, internet, person, phone_number, ssn
from persistent.list import PersistentList

from src.domain.arhitektura_kluba import Clan, Ekipa, Oddelek, Klub, Kontakt, TipKontakta
from src.domain.bancni_racun import Transakcija, TipTransakcije, BancniRacun, KategorijaTransakcije

db = ZODB.DB(None)


class Root:
	klubi: PersistentList | list[Klub]
	kontakti: PersistentList | list[Clan]
	clani: PersistentList | list[Clan]
	ekipe: PersistentList | list[Ekipa]
	oddelki: PersistentList | list[Oddelek]

	def __init__(self, root):
		for k, v in Root.__annotations__.items():
			setattr(self, k, getattr(root, k))


@contextmanager
def transaction(note: str = None) -> Iterator[Root]:
	with db.transaction(note=note) as con:
		yield Root(con.root)


fake: Union[address.Provider, company.Provider, date_time.Provider, internet.Provider, person.Provider,
            phone_number.Provider,
            ssn.Provider,
            Faker] = Faker("sl_SI")


def seed(root: Root, kontakti: int, clani: int, ekipe: int, oddeleki: int, klubi: int, transakcije: int, bancni_racun: int):
	root.kontakti = PersistentList()
	for i in range(kontakti):
		root.kontakti.append(Kontakt(
			ime=fake.first_name(),
			priimek=fake.last_name(),
			tip=choice(list(TipKontakta)),
			email=[str(fake.email) for _ in range(randint(0, 4))],
			telefon=[fake.phone_number() for _ in range(randint(0, 4))]
		))

	root.clani = PersistentList()
	for i in range(clani):
		root.clani.append(Clan(
			ime=fake.first_name(),
			priimek=fake.last_name(),
			rojen=fake.date_this_century(before_today=True),
			email=fake.email(),
			telefon=[fake.phone_number() for i in range(randint(1, 3))],
			vpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))],
			izpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))],
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

	root.transakcija = PersistentList()
	for i in range(transakcije):
		znesek = uniform(0, 1000)
		placano = choice([0, znesek] + [uniform(0, int(znesek)) for _ in range(8)])
		root.transakcija.append(Transakcija(
			tip=choice(list(TipTransakcije)),
			kategorija=choice(list(KategorijaTransakcije)),
			rok=fake.date_this_month(before_today=True, after_today=True),
			opis=fake.catch_phrase(),
			znesek=znesek,
			placano=placano)
		)

	root.bancni_racun = PersistentList()
	for i in range(bancni_racun):
		root.bancni_racun.append(BancniRacun(
			ime=fake.catch_phrase(),
			stevilka=fake.numerify("SI##############"),
			transakcije=choices(root.transakcija, k=50)
		))


def init():
	with db.transaction(note="seed.migrate") as con:
		seed(con.root, kontakti=120, clani=60, ekipe=20, oddeleki=6, klubi=2, transakcije=180, bancni_racun=3)


init()
with transaction() as root:
	print(root.klubi)
