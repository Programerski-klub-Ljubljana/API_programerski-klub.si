from dataclasses import dataclass

from autologging import traced

from app import CONST


@dataclass
@traced
class Form:
	subject: str
	msg: str

	def __post_init__(self):
		self.subject = f'{CONST.klub} | {self.subject}'


vpis = Form('Potrdilo ob vpisu', 'Preveri če si dobil potrditveni email.')
