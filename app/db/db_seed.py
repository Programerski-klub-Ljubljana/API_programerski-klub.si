from datetime import timedelta
from random import choice, randint, uniform

from autologging import traced

from core.cutils import fake
from core.domain._entity import Log
from core.domain._enums import LogLevel, LogTheme
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, Oseba, Ekipa, Oddelek, Klub, TipValidacije, TipOsebe
from core.domain.bancni_racun import Transakcija, TipTransakcije, KategorijaTransakcije, Bancni_racun
from core.domain.oznanila_sporocanja import Objava, TipObjave, Sporocilo, TipSporocila
from core.domain.srecanja_dogodki import Dogodek, TipDogodka
from core.domain.vaje_naloge import Naloga, Tezavnost, Test


@traced
def arhitektura_kluba(root, **kwargs):
	for _ in range(kwargs['clani']):
		kontakti = []
		for i in range(randint(2, kwargs['kontakti'])):
			tip = TipKontakta.random()
			data = str(fake.email) if tip == TipKontakta.EMAIL else fake.phone_number()
			kontakt = Kontakt(data=data, tip=tip, validacija=TipValidacije.random())
			kontakti.append(kontakt)

		root.save(Oseba(
			ime=fake.first_name(),
			priimek=fake.last_name(),
			geslo=kwargs['geslo'],
			tip_osebe=TipOsebe.random(),
			kontakti=kontakti,
			rojen=fake.date_this_century(before_today=True),
			vpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))],
			izpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))]))

	for _ in range(kwargs['ekipe']):
		root.save(Ekipa(
			ime=fake.catch_phrase(),
			opis=fake.sentence(9)))

	for _ in range(kwargs['oddeleki']):
		root.save(Oddelek(
			ime=fake.catch_phrase(),
			opis=fake.sentence(9),
			ekipe=root.ekipa.random(k=randint(1, 5))))

	for _ in range(kwargs['klubi']):
		root.save(Klub(
			clanarina=uniform(15, 60),
			ime=fake.catch_phrase(),
			oddelki=root.oddelek))


@traced
def bancni_racun(root, **kwargs):
	for _ in range(kwargs['transakcije']):
		znesek = round(uniform(0, 1000), 3)
		placano = choice([0, znesek] + [round(uniform(0, int(znesek))) for _ in range(8)])
		root.save(Transakcija(
			tip=TipTransakcije.random(),
			kategorija=KategorijaTransakcije.random(),
			rok=fake.date_this_month(after_today=True),
			opis=fake.sentence(9),
			znesek=znesek,
			placano=placano))

	for _ in range(kwargs['bancni_racun']):
		root.save(Bancni_racun(
			ime=fake.catch_phrase(),
			stevilka=fake.numerify("SI##############"),
			transakcije=root.transakcija.random(k=50)))


@traced
def oznanila_sporocanja(root, **kwargs):
	for _ in range(kwargs['objave']):
		root.save(Objava(
			tip=TipObjave.random(),
			naslov=fake.catch_phrase(),
			opis=fake.sentence(9),
			vsebina=fake.sentence(50)))

	for _ in range(kwargs['sporocila']):
		root.save(Sporocilo(
			tip=TipSporocila.random(),
			vsebina=fake.sentence(50)))


@traced
def srecanja_dogodki_tekme(root, **kwargs):
	for _ in range(kwargs['dogodek']):
		zacetek = fake.date_time_this_year(after_now=True)
		root.save(Dogodek(
			ime=fake.catch_phrase(),
			trajanje=randint(30, 240),
			opis=fake.sentence(20),
			tip=TipDogodka.random(),
			zacetek=zacetek,
			konec=zacetek + timedelta(minutes=randint(30, 300))))


@traced
def vaje_naloge(root, **kwargs):
	for _ in range(kwargs['naloge']):
		root.save(Naloga(
			ime=fake.catch_phrase(),
			opis=fake.sentence(20),
			stevilo_algoritmov=randint(1, 10),
			tezavnost_algoritmov=Tezavnost.random(),
			tezavnost_struktur=Tezavnost.random(),
			koda=fake.sentence(30),
			test=fake.sentence(30)))

	for _ in range(kwargs['test']):
		root.save(Test(
			ime=fake.catch_phrase(),
			opis=fake.sentence(20),
			naloge=root.naloga.random(k=randint(5, 30))))


@traced
def logs(root, **kwargs):
	for name, table in root.__dict__.items():
		for entity in table:
			for _ in range(randint(0, kwargs['logs'])):
				log = Log(
					nivo=LogLevel.random(),
					tema=LogTheme.random(),
					sporocilo=fake.sentence(20))
				root.save(log)
				entity._dnevnik.append(log)


@traced
def povezave(root, **kwargs):
	tables = list(root.__dict__.values())
	for i in range(len(tables)):
		if len(tables[i]) == 0:
			continue
		for j in range(len(tables)):
			if len(tables[j]) == 0:
				continue

			parents = tables[i].random(k=randint(0, kwargs['elementi']))
			for parent in parents:
				for _ in range(randint(0, kwargs['povezave'])):
					child = tables[j].random()
					parent.povezi(child)
