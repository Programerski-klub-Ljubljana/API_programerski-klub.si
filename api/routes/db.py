from autologging import traced

from api import autils
from app import APP
from core import cutils

router = autils.router(__name__)


@traced
@router.get("/{table}/{path:path}")
def get_table_data(table: str, path: str = None, page: int = 0, per_page: int = 10, max_depth: int = 3, max_width: int = 10):
	db = APP.cases.vrni_vsebino_baze()
	return cutils.call(db.exe, **locals())
