from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Vloga_Tip(str, Enum):
	TRENER = 'TRENER'
	UCENEC = 'UCENEC'
	ASISTENT = "ASISTENT"
	TEKMOVALEC = 'TEKMOVALEC'
	OBISKOVALEC = 'OBISKOVALEC'


class Vloga(SQLModel, table=True):

	tip: Vloga_Tip
	clan: int = Field(foreign_key='clan.id')
	dodeljena: datetime = Field(default_factory=datetime.utcnow, nullable=False)

	clan: Optional[int] = Field(default=None, foreign_key="clan.id")
	dogodek: Optional[int] = Field(default=None, foreign_key="dogodek.id")
	ekipa: Optional[int] = Field(default=None, foreign_key="ekipa.id")
	kontakt: Optional[int] = Field(default=None, foreign_key="kontakt.id")
	naloga: Optional[int] = Field(default=None, foreign_key="naloga.id")
	objava: Optional[int] = Field(default=None, foreign_key="objava.id")
	oddelek: Optional[int] = Field(default=None, foreign_key="oddelek.id")
	sporocilo: Optional[int] = Field(default=None, foreign_key="sporocilo.id")
	transakcija: Optional[int] = Field(default=None, foreign_key="transakcija.id")
