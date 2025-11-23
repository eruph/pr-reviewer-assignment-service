from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.users.users_service import UserService
from app.domain.models import (
    ErrorResponse,
    ErrorDetail,
    ErrorCode,
)
from app.infrastructure.db.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/setIsActive",
    response_model=dict,
    responses={
        404: {"model": ErrorResponse}
    }
)
def set_user_active(data: dict, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        user_pyd = service.set_user_active(data)
        return {"user": user_pyd}
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


@router.get(
    "/getReview",
    response_model=dict,
)
def get_user_reviews(user_id: str, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        result = service.get_user_reviews(user_id)
        return result
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
