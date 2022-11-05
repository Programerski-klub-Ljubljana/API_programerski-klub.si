from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

class Tip(str, Enum):
	EMAIL = 'EMAIL'
	SMS = 'SMS'
	KONTAKT = 'KONTAKT'

class Sporocilo(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	tip: Tip
	template: str
	body: str
	odgovor_na: Optional[int] = Field(default=None, foreign_key="sporocilo.id")
	ustvarjeno: datetime = Field(default_factory=datetime.utcnow, nullable=False)
