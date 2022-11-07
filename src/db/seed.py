from datetime import timedelta
from random import choice, randint, choices, uniform
from typing import Union

from faker import Faker
from faker.providers import address, company, date_time, internet, person, phone_number, ssn, lorem

from src.db import Root, db
from src.db.entity import Log
from src.db.enums import LogLevel, LogTheme
from src.domain.arhitektura_kluba import Kontakt, TipKontakta, Clan, Ekipa, Oddelek, Klub
from src.domain.bancni_racun import Transakcija, TipTransakcije, KategorijaTransakcije, BancniRacun
from src.domain.oznanila_sporocanja import Objava, TipObjave, Sporocilo, TipSporocila
from src.domain.srecanja_dogodki import Dogodek, TipDogodka
from src.domain.vaje_naloge import Naloga, Tezavnost, Test

fake: Union[
	address.Provider,
	company.Provider,
	date_time.Provider,
	internet.Provider,
	person.Provider,
	phone_number.Provider,
	ssn.Provider,
	lorem.Provider,
	Faker
] = Faker("sl_SI")


def arhitektura_kluba(root: Root, **kwargs):
	for _ in range(kwargs['kontakti']):
		root.kontakti.append(Kontakt(
			ime=fake.first_name(),
			priimek=fake.last_name(),
			tip=choice(list(TipKontakta)),
			email=[str(fake.email) for _ in range(randint(0, 4))],
			telefon=[fake.phone_number() for _ in range(randint(0, 4))]))

	for _ in range(kwargs['clani']):
		root.clani.append(Clan(
			ime=fake.first_name(),
			priimek=fake.last_name(),
			rojen=fake.date_this_century(before_today=True),
			email=fake.email(),
			telefon=[fake.phone_number() for _ in range(randint(1, 3))],
			vpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))],
			izpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))], ))

	for _ in range(kwargs['ekipe']):
		root.ekipe.append(Ekipa(
			ime=fake.catch_phrase(),
			opis=fake.sentence(9)))

	for _ in range(kwargs['oddeleki']):
		root.oddelki.append(Oddelek(
			ime=fake.catch_phrase(),
			opis=fake.sentence(9),
			ekipe=choices(root.ekipe, k=randint(1, 10))))

	for _ in range(kwargs['klubi']):
		root.klubi.append(Klub(
			ime=fake.catch_phrase(),
			oddelki=root.oddelki))


def bancni_racun(root: Root, **kwargs):
	for _ in range(kwargs['transakcije']):
		znesek = round(uniform(0, 1000), 3)
		placano = choice([0, znesek] + [round(uniform(0, int(znesek))) for _ in range(8)])
		root.transakcije.append(Transakcija(
			tip=choice(list(TipTransakcije)),
			kategorija=choice(list(KategorijaTransakcije)),
			rok=fake.date_this_month(after_today=True),
			opis=fake.sentence(9),
			znesek=znesek,
			placano=placano))

	for _ in range(kwargs['bancni_racun']):
		root.bancni_racun.append(BancniRacun(
			ime=fake.catch_phrase(),
			stevilka=fake.numerify("SI##############"),
			transakcije=choices(root.transakcije, k=50)))


def oznanila_sporocanja(root: Root, **kwargs):
	for _ in range(kwargs['objave']):
		root.objava.append(Objava(
			tip=choice(list(TipObjave)),
			naslov=fake.catch_phrase(),
			opis=fake.sentence(9),
			vsebina=fake.sentence(50)))

	for _ in range(kwargs['sporocila']):
		root.sporocilo.append(Sporocilo(
			tip=choice(list(TipSporocila)),
			vsebina=fake.sentence(50)))


def srecanja_dogodki_tekme(root: Root, **kwargs):
	for _ in range(kwargs['dogodek']):
		zacetek = fake.date_time_this_year(after_now=True)
		root.dogodki.append(Dogodek(
			ime=fake.catch_phrase(),
			trajanje=randint(30, 240),
			opis=fake.sentence(20),
			tip=choice(list(TipDogodka)),
			zacetek=zacetek,
			konec=zacetek + timedelta(minutes=randint(30, 300))))


def vaje_naloge(root: Root, **kwargs):
	for _ in range(kwargs['naloge']):
		root.naloge.append(Naloga(
			ime=fake.catch_phrase(),
			opis=fake.sentence(20),
			stevilo_algoritmov=randint(1, 10),
			tezavnost_algoritmov=choice(list(Tezavnost)),
			tezavnost_struktur=choice(list(Tezavnost)),
			koda=fake.sentence(30),
			test=fake.sentence(30)))

	for _ in range(kwargs['test']):
		root.testi.append(Test(
			ime=fake.catch_phrase(),
			opis=fake.sentence(20),
			naloge=choices(root.naloge, k=randint(5, 30))
		))


def logs(root: Root, **kwargs):
	for name, table in root.__dict__.items():
		for entity in table:
			for _ in range(randint(0, kwargs['logs'])):
				log = Log(
					nivo=choice(list(LogLevel)),
					tema=choice(list(LogTheme)),
					sporocilo=fake.sentence(20),
					_ustvarjen=fake.date_time_this_year(after_now=True))
				root.logs.append(log)
				entity._dnevnik.append(log)


def init():
	with db.transaction(note="seed.migrate") as con:
		root = Root(con.root)
		arhitektura_kluba(root, kontakti=120, clani=60, ekipe=20, oddeleki=6, klubi=4)
		bancni_racun(root, transakcije=180, bancni_racun=3)
		oznanila_sporocanja(root, objave=50, sporocila=200)
		srecanja_dogodki_tekme(root, dogodek=50)
		vaje_naloge(root, naloge=400, test=30)
		logs(root, logs=20)
	with db.transaction(note="seed.migrate") as con:
		print(con.root.kontakti[0])
