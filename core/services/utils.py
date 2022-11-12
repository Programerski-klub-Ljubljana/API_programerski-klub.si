from dataclasses import dataclass


@dataclass
class Validation:
	data: str
	ok: bool
