from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.teams.teams_service import TeamService
from app.domain.models import (
    Team,
    ErrorResponse,
    ErrorDetail,
    ErrorCode,
)
from app.infrastructure.db.database import get_db

router = APIRouter(prefix="/team", tags=["Teams"])

@router.post("/add", response_model=Team, status_code=201)
def add_team(team: Team, db: Session = Depends(get_db)):
    service = TeamService(db)
    try:
        team_pyd = service.add_team(team)
        return team_pyd
    except ValueError as e:
        error_code = e.args[0]
        if error_code == ErrorCode.TEAM_EXISTS:
            status_code = 400
            message = "team_name already exists"
        elif error_code == "DATABASE_ERROR":
            status_code = 500
            message = "Error creating team or users"
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")

        raise HTTPException(
            status_code=status_code,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code=error_code,
                    message=message
                )
            ).model_dump()
        )

@router.get("/get", response_model=Team)
def get_team(team_name: str, db: Session = Depends(get_db)):
    service = TeamService(db)
    try:
        team_pyd = service.get_team(team_name)
        return team_pyd
    except ValueError as e:
        error_code = e.args[0]
        if error_code == ErrorCode.NOT_FOUND:
            status_code = 404
            message = "resource not found"
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")

        raise HTTPException(
            status_code=status_code,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code=error_code,
                    message=message
                )
            ).model_dump()
        )
