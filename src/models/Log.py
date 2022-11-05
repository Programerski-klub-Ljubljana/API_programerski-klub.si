from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Log_Tip(str, Enum):
	VPIS = 'VPIS'
	IZPIS = 'IZPIS'
	KONTAKT = 'KONTAKT'


class Log_Level(str, Enum):
	INFO = 'INFO'
	WARNING = 'WARNING'
	ERROR = 'ERROR'


class Log_Service(str, Enum):
	EMAIL = 'EMAIL'
	DB = 'DB',
	API = 'API'


class Log(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)

	level: Log_Level
	service: Log_Service
	tip: Log_Tip
	msg: str

	clan: Optional[int] = Field(default=None, foreign_key="clan.id")
	dogodek: Optional[int] = Field(default=None, foreign_key="dogodek.id")
