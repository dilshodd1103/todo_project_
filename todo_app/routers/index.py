from fastapi import APIRouter

router = APIRouter(tags=["index"])


@router.get("/")
async def index() -> dict:
    return {"message": "Web sayt ishlayabdi"}
