# app/api/v1/endpoints/stats.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.stats.stats_service import StatsService
from app.domain.models import (
    StatsResponse,
    ErrorResponse,
    ErrorDetail,
)
from app.infrastructure.db.database import get_db

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get(
    "/reviewer_assignments",
    response_model=StatsResponse,
    responses={
        500: {"model": ErrorResponse}
    }
)
def get_reviewer_assignment_stats(db: Session = Depends(get_db)):
    service = StatsService(db)
    try:
        stats = service.get_reviewer_assignment_counts()
        return StatsResponse(reviewer_assignment_counts=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorResponse(
            error=ErrorDetail(
                code="DATABASE_ERROR",
                message="Database error"
            )
        ).model_dump())

