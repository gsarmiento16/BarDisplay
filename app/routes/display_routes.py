from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/t/{code}")
async def tenant_display(code: str) -> FileResponse:
    return FileResponse("web/index.html")
