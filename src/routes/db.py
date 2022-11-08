from fastapi import APIRouter

from src.db import Transaction
from src.utils import is_iterable, todict, error

router = APIRouter()


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


@router.get("/{table}/{path:path}")
def get_path(table: str, path: str=None, page: int | None = 0):
	try:
		with Transaction() as root:
			result = nested_path(getattr(root, table), path)
			start = 10 * page
			end = 10 * (page + 1)
			result = result[start:end] if is_iterable(result) else result
			return todict(result, max_depth=3)
	except Exception as err:
		return error(err)
