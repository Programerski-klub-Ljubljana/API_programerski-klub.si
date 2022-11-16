from random import randint
from typing import Union

from faker import Faker
from faker.providers import address, company, date_time, internet, person, phone_number, ssn, lorem

from core.domain.arhitektura_kluba import Clan

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

geslo = '$2b$12$I/pWjen11YetXJRmHfObrevezyy3BRDaznrzKGvQ3d73UTQ53UbNK'  # geslo=geslo


clan = Clan(
	ime='Uroš',
	priimek='Jarc',
	geslo=geslo,
	rojen=fake.date_this_century(before_today=True),
	vpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))],
	izpisi=[fake.date_time_this_decade(before_now=True) for _ in range(randint(0, 5))])
