from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.pull_requests.pull_requests_service import PullRequestService
from app.domain.models import (
    ErrorResponse,
    ErrorDetail,
    ErrorCode,
    ReassignResponse
)
from app.infrastructure.db.database import get_db

router = APIRouter(prefix="/pullRequest", tags=["PullRequests"])

@router.post("/create", status_code=201, response_model=dict)
def create_pr(data: dict, db: Session = Depends(get_db)):
    service = PullRequestService(db)
    try:
        pr_pyd = service.create_pull_request(data)
        return {"pr": pr_pyd}
    except ValueError as e:
        error_code = e.args[0]
        if error_code == ErrorCode.PR_EXISTS:
            status_code = 409
            message = "PR id already exists"
        elif error_code == ErrorCode.NOT_FOUND:
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

@router.post("/merge", response_model=dict)
def merge_pr(data: dict, db: Session = Depends(get_db)):
    service = PullRequestService(db)
    try:
        pr_pyd = service.merge_pull_request(data)
        return {"pr": pr_pyd}
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

@router.post("/reassign", response_model=ReassignResponse)
def reassign_pr(data: dict, db: Session = Depends(get_db)):
    service = PullRequestService(db)
    try:
        response = service.reassign_reviewer(data)
        return response
    except ValueError as e:
        error_code = e.args[0]
        if error_code == ErrorCode.NOT_FOUND:
            status_code = 404
            message = "resource not found"
        elif error_code == ErrorCode.PR_MERGED:
            status_code = 409
            message = "cannot reassign on merged PR"
        elif error_code == ErrorCode.NOT_ASSIGNED:
            status_code = 409
            message = "reviewer is not assigned to this PR"
        elif error_code == ErrorCode.NO_CANDIDATE:
            status_code = 409
            message = "no active replacement candidate in team"
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
