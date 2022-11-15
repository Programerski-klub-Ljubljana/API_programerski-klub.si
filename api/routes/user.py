from api import autils

router = autils.router(__name__)


@router.post("/login")
async def login():
	return {"access_token": 'access_token', "token_type": "bearer"}


@router.get("/info")
async def info():
	return 'current_user'


@router.get("/items")
async def items():
	return [{"item_id": "Foo", "owner": 'current_user.username'}]


@router.get("/status")
async def status():
	return {"status": "ok"}
