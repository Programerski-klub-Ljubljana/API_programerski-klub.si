from datetime import date
from pathlib import Path

from dateutil.relativedelta import *
from fastapi import APIRouter


def root_path(*paths) -> Path:
	return Path(__file__).parent.parent.joinpath(*paths)


def age(year: int, month: int, day: int) -> float:
	today = date.today()
	event = date(year=year, month=month, day=day)
	dt = relativedelta(today, event)
	return dt.years + dt.months / 12 + dt.days / 365.25


def is_iterable(ele: object) -> bool:
	return hasattr(ele, "__iter__") and not isinstance(ele, str)


def is_object(ele: object) -> bool:
	return hasattr(ele, "__dict__")


def todict(obj, classkey=None, depth=0, max_depth=1, ignore: list[str] = ('_dnevnik', '_povezave')):
	if classkey in ignore:
		return 'IGNORE'

	if is_iterable(obj):
		if depth >= max_depth:
			return ['MAX_DEPTH']
		return [todict(v, classkey, depth + 1, max_depth, ignore) for v in obj]
	elif is_object(obj):
		if depth >= max_depth:
			return 'MAX_DEPTH'
		data = {}
		for key, value in obj.__dict__.items():
			if not callable(value) and key not in ignore:
				data[key] = todict(value, classkey, depth, max_depth, ignore)
		if classkey is not None and hasattr(obj, "__class__"):
			data[classkey] = obj.__class__.__name__
		return data
	else:
		return obj


def error(exception) -> dict:
	return {'error': str(exception)}


def nested_path(data, value=None) -> object:
	if value is None:
		return data
	path = value.split("/")
	path.remove('')
	ref = data
	while path:
		element, path = path[0], path[1:]
		if is_iterable(ref):
			ref = ref[int(element)]
		else:
			ref = getattr(ref, element)
	return ref


def router(_name_) -> APIRouter:
	name = _name_.split('.')[-1]
	return APIRouter(prefix=f'/{name}', tags=[name])
