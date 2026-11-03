from fastapi import APIRouter, status, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db import get_session


health_router = APIRouter(
    prefix="/health",
    tags=["health"]
)

@health_router.get("/live", status_code=status.HTTP_200_OK)
def api_health_check():
    return {"status": "ok"}


@health_router.get("/ready", status_code=status.HTTP_200_OK)
def db_health_check():
    try:
        with get_session() as session:
            session.execute(text("SELECT 1"))
            
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    return {"status": "ok"}    