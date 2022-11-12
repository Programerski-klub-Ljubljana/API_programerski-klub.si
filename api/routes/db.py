from api import utils
from api.db import Transaction

router = utils.router(__name__)


@router.get("/{table}/{path:path}")
def get_table_data(table: str, path: str | None = None, page: int | None = 0):
	try:
		with Transaction() as root:
			result = utils.nested_path(getattr(root, table), path)
			start = 10 * page
			end = 10 * (page + 1)
			result = result[start:end] if utils.is_iterable(result) else result
			return utils.todict(result, max_depth=3)
	except Exception as err:
		return utils.error(err)
