from datetime import datetime

from sqlmodel import create_engine, SQLModel, Session

from src.models.Clan import Clan
from src.models.Oseba import Skrbnik
from src.models.Sporocilo import Tip, Sporocilo

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def migration():
	SQLModel.metadata.create_all(engine)


def seed():
	with Session(engine) as session:
		urosjarc = Clan(
			ime='Uros',
			priimek='Jarc',
			email='jar.fmf@gmail.com',
			telefon='051240885',
			rojen=datetime(1992, 5, 24),
			vpisan=datetime(2022, 11, 5),
			izpisan=None,
			skrbnik_id=None,
		)
		mojcajarc = Skrbnik(
			ime='Mojca',
			priimek='Jarc',
			email='mojca.jarc@gmail.com',
			telefon='041327791'
		)
		jernejjarc = Clan(
			ime='Jernej',
			priimek='Jarc',
			email='jernej.jko@gmail.com',
			telefon='051251884',
			rojen=datetime(2000, 5, 24),
			vpisan=datetime(2022, 10, 5),
			izpisan=None,
			skrbnik_id=mojcajarc.id,
		)
		sporocilo1 = Sporocilo(
			tip=Tip.EMAIL,
			template='email_vpis.html',
			body=str({'name': 'Uros', 'priimek': 'Jarc'})
		)
		session.add(urosjarc)
		session.add(jernejjarc)
		session.add(mojcajarc)
		session.commit()
