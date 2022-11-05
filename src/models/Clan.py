from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel




class Clan(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)

	# INFO
	ime: str
	priimek: str
	rojen: datetime

	# KONTAKT
	email: Optional[str] = None
	telefon: Optional[str] = None

	# DATUMI
	vpisan: datetime = Field(default_factory=datetime.utcnow, nullable=True)
	izpisan: Optional[datetime] = Field(nullable=True)
	ustvarjen: datetime = Field(default_factory=datetime.utcnow)
