from datetime import datetime

from sqlmodel import create_engine, SQLModel, Session

from src.models.Clan import *
from src.models.Dogodek import *
from src.models.Ekipa import *
from src.models.Kontakt import *
from src.models.Log import *
from src.models.Naloga import *
from src.models.Objava import *
from src.models.Sporocilo import *
from src.models.Transakcija import *

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def migration():
	SQLModel.metadata.create_all(engine)


def seed():
	with Session(engine) as session:
		session.commit()
