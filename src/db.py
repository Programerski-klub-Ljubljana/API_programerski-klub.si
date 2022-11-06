from sqlmodel import create_engine, Session

from src.domain.Clan import *
from src.domain.Ekipa import *
from src.domain.Naloga import *
from src.domain.Transakcija import *

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def migration():
	SQLModel.metadata.create_all(engine)


def seed():
	with Session(engine) as session:
		session.commit()
