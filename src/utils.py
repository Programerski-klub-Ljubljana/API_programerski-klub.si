from datetime import date
from pathlib import Path

from dateutil.relativedelta import *


def rootPath(*paths) -> Path:
	return Path(__file__).parent.parent.joinpath(*paths)


def age(year: int, month: int, day: int) -> float:
	today = date.today()
	event = date(year=year, month=month, day=day)
	dt = relativedelta(today, event)
	return dt.years + dt.months / 12 + dt.days / 365.25


def todict(obj, classkey=None, depth=0, max_depth=4):
	if isinstance(obj, dict):
		data = {}
		for (k, v) in obj.items():
			data[k] = todict(v, classkey, depth + 1, max_depth)
		return data
	elif hasattr(obj, "__iter__") and not isinstance(obj, str):
		if depth >= max_depth:
			return ['MAX_DEPTH']
		return [todict(v, classkey, depth, max_depth) for v in obj]
	elif hasattr(obj, "__dict__"):
		if depth >= max_depth:
			return ['MAX_DEPTH']
		data = {}
		for key, value in obj.__dict__.items():
			if not callable(value) and not key.startswith('_'):
				data[key] = todict(value, classkey, depth + 1, max_depth)
		if classkey is not None and hasattr(obj, "__class__"):
			data[classkey] = obj.__class__.__name__
		return data
	else:
		return obj
