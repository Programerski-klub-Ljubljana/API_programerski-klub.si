import ast
import inspect
import os
from dataclasses import field
from datetime import date
from pathlib import Path
from typing import Mapping, Union, Callable

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
	return hasattr(ele, "__dict__") and not is_mappable(ele) and not is_iterable(ele)


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
		ignore: list[str] = ('_p_logs', '_connections')):

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
				data[key] = object_json(obj=value, obj_key=obj_key, depth=depth + 1, max_depth=max_depth, max_width=max_width, ignore=ignore)
		# ======================
		return data
	else:
		return obj


def call(func, **kwargs):
	sign = inspect.signature(func).parameters.values()
	sign = set([val.name for val in sign])

	common_args = sign.intersection(kwargs.keys())
	filtered_dict = {key: kwargs[key] for key in common_args}

	return func(**filtered_dict)


def list_field(*values: any):
	return field(default_factory=lambda: list(values))


def lambda_src(func: Callable):
	"""
		https://gist.github.com/Xion/617c1496ff45f3673a5692c3b0e3f75a
		http://xion.io/post/code/python-get-lambda-code.html
	"""
	try:
		source_lines, _ = inspect.getsourcelines(func)
	except (IOError, TypeError):
		return None

	if len(source_lines) != 1:
		return None

	source_text = os.linesep.join(source_lines).strip()

	source_ast = ast.parse(source_text)
	lambda_node = next((node for node in ast.walk(source_ast) if isinstance(node, ast.Lambda)), None)
	if lambda_node is None:
		return None

	lambda_text = source_text[lambda_node.col_offset:]
	lambda_body_text = source_text[lambda_node.body.col_offset:]
	min_length = len('lambda:_')
	while len(lambda_text) > min_length:
		try:
			code = compile(lambda_body_text, '<unused filename>', 'eval')
			if len(code.co_code) == len(func.__code__.co_code):
				return lambda_text
		except SyntaxError:
			pass
		lambda_text = lambda_text[:-1]
		lambda_body_text = lambda_body_text[:-1]

	return None


def kwargs_str(**kwargs) -> str:
	args = []
	for k, v in kwargs.items():
		if not k.startswith('__') and k not in ['self']:
			if isinstance(v, Callable):
				args.append(f"{k}={lambda_src(v)}")
			elif isinstance(v, str):
				args.append(f"{k}='{v}'")
			else:
				args.append(f"{k}={v}")

	return ', '.join(args)


def args_str(*args) -> str:
	arg = []
	for i, v in enumerate(args):
		if isinstance(v, Callable):
			arg.append(f"{lambda_src(v)}")
		elif isinstance(v, str):
			arg.append(f"'{v}'")
		else:
			arg.append(f"{v}")

	return ', '.join(arg)
