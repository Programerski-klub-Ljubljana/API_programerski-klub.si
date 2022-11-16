from api import autils
from app import APP
from core import cutils

router = autils.router(__name__)


@router.get("/{table}/{path:path}")
def get_table_data(table: str, path: str = None, page: int = 0, per_page: int = 10, max_depth: int = 3, max_width: int = 10):
	db = APP.useCases.db_path()
	return db.invoke(**cutils.filter_dict(db.invoke, locals()))
