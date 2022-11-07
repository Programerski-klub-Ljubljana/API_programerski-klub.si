from fastapi import APIRouter

router = APIRouter()

@router.get("/payments/stripe")
def transaction():
	return {}
