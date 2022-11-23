import inspect
from datetime import date
from pathlib import Path
from typing import Mapping, Union

from dateutil.relativedelta import *
from faker import Faker
from faker.providers import address, company, date_time, internet, person, phone_number, ssn, lorem

fake: Union[
	address.Provider,
	company.Provider,
	date_time.Provider,
	internet.Provider,
	person.Provider,
	phone_number.Provider,
	ssn.Provider,
	lorem.Provider,
	Faker
] = Faker("sl_SI")


def root_path(*paths) -> Path:
	return Path(__file__).parent.parent.joinpath(*paths)


def age(year: int, month: int, day: int) -> float:
	today = date.today()
	event = date(year=year, month=month, day=day)
	dt = relativedelta(today, event)
	return dt.years + dt.months / 12 + dt.days / 365.25


def is_iterable(ele: object) -> bool:
	return hasattr(ele, "__iter__") and not is_mappable(ele) and not isinstance(ele, str)


def is_mappable(ele: object) -> bool:
	return isinstance(ele, Mapping)


def is_object(ele: object) -> bool:
	return hasattr(ele, "__dict__") and not is_iterable(ele)


def object_path(data: list | dict | object, path: str = None) -> object:
	if path in [None, '/', '']:
		return data
	path = path.split("/")
	path = list(filter(lambda x: x != '', path))
	ref = data
	while path:
		element, path = path[0], path[1:]
		if is_iterable(ref):
			ref = ref[int(element)]
		elif is_mappable(ref):
			ref = ref[element]
		else:
			ref = getattr(ref, element)
	return ref


def object_json(
		obj: object | list,
		obj_key: str = None,
		depth: int = 0,
		max_depth: int = 3,
		max_width: int = 10,
		ignore: list[str] = ('_dnevnik', '_povezave')):
	if is_iterable(obj):  # LIST PROCESSING...
		if depth >= max_depth:
			return 'MAX_DEPTH_LIST'

		# LIMIT WIDTH OF INTERNAL LIST
		returned = []
		for v in list(obj)[:max_width]:
			returned.append(object_json(obj=v, obj_key=obj_key, depth=depth + 1, max_depth=max_depth, max_width=max_width, ignore=ignore))

		if len(obj) > max_width:
			returned.append('MAX_WIDTH')
		# ============================
		return returned

	elif is_object(obj):  # OBJECT PROCESSING
		if depth >= max_depth:
			return 'MAX_DEPTH_OBJECT'

		# PROCESSING OBJECT KEYS
		data = {}
		for key, value in obj.__dict__.items():
			if not callable(value) and key not in ignore:
				data[key] = object_json(obj=value, obj_key=obj_key, depth=depth + 1, max_depth=max_depth, ignore=ignore)
		# ======================
		return data
	else:
		return obj


def filter_dict(func, kwarg_dict):
	sign = inspect.signature(func).parameters.values()
	sign = set([val.name for val in sign])

	common_args = sign.intersection(kwarg_dict.keys())
	filtered_dict = {key: kwarg_dict[key] for key in common_args}

	return filtered_dict
