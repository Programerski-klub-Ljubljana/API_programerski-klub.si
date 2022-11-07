from fastapi import APIRouter

from src import db
from src.utils import is_iterable, todict

router = APIRouter()


def nested_path(data, value=None) -> object:
	if value is None:
		return data
	path = value.split("/")
	ref = data
	while path:
		element, path = path[0], path[1:]
		if is_iterable(ref):
			ref = ref[int(element)]
		else:
			ref = getattr(ref, element)
	return ref


@router.get("/db/{path:path}")
def db(path: str | None = None, page: int | None = 0):
	print(locals())
	try:
		with db.transaction() as root:
			result = nested_path(root, path)
			start = 10 * page
			end = 10 * (page + 1)
			result = result[start:end] if is_iterable(result) else result
			return todict(result, max_depth=3)
	except Exception as err:
		return error(err)
