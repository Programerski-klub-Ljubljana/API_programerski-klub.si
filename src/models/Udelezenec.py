from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Tip(str, Enum):
	TRENER = 'TRENER'
	UCENEC = 'UCENEC'
	ASISTENT = "ASISTENT"
	TEKMOVALEC = 'TEKMOVALEC'
	OBISKOVALEC = 'OBISKOVALEC'

class Udelezenec(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)

	# POVEZAVE
	tip: Tip
	clan: Optional[int] = Field(default=None, foreign_key="clan.id")
	dogodek: int = Field(default=None, foreign_key="dogodek.id")
