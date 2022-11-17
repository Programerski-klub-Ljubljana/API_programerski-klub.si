from datetime import datetime, timedelta
from random import randint
from typing import Union

from faker import Faker
from faker.providers import address, company, date_time, internet, person, phone_number, ssn, lorem

from core.domain.arhitektura_kluba import Clan
from core.domain.bancni_racun import Transakcija, TipTransakcije, KategorijaTransakcije

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

geslo = '$2b$12$HpUrAvHs/S5A4tm38LmCdOMSSSKElmgTiGShQ4OXYk2c0QiN2WyRu'
geslo_raw = 'geslo'


def init_clan(
		ime: str = 'kožušček',
		priimek: str = 'šđžčć',
		rojstro_delta_days: int = 20 * 365,
		vpisi: list[datetime] = None,
		izpisi: list[datetime] = None):
	return Clan(
		ime=ime,
		priimek=priimek,
		geslo=geslo,
		rojen=datetime.utcnow() - timedelta(days=rojstro_delta_days),
		vpisi=[] if vpisi is not None else [fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))],
		izpisi=[] if izpisi is not None else [fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))])


def init_transakcija(prihodek=True, znesek: float = 0, placano: float = 0):
	return Transakcija(
		tip=TipTransakcije.PRIHODEK if prihodek else TipTransakcije.ODHODEK,
		kategorija=KategorijaTransakcije.random(),
		rok=fake.date_this_month(after_today=True),
		opis=fake.sentence(9),
		znesek=znesek,
		placano=placano)
