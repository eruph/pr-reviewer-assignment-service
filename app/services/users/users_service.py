from typing import Dict, Any
from sqlalchemy.orm import Session
from app.infrastructure.db.models import UserORM, PullRequestORM
from app.domain.models import (
    User as PydanticUser,
    user_orm_to_pydantic,
    pr_orm_to_pydantic_short,
    ErrorCode
)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def set_user_active(self, data: Dict[str, Any]) -> PydanticUser:
        user_id = data["user_id"]
        is_active = data["is_active"]

        user_orm = self.db.query(UserORM).filter(UserORM.user_id == user_id).first()

        if not user_orm:
            raise ValueError(ErrorCode.NOT_FOUND)

        user_orm.is_active = is_active
        self.db.commit()
        self.db.refresh(user_orm)

        return user_orm_to_pydantic(user_orm)

    def get_user_reviews(self, user_id: str) -> Dict[str, Any]:
        user_orm = self.db.query(UserORM).filter(UserORM.user_id == user_id).first()
        if not user_orm:
            raise ValueError(ErrorCode.NOT_FOUND)

        prs_orm = self.db.query(PullRequestORM).filter(
            PullRequestORM.reviewers.any(UserORM.user_id == user_id)
        ).all()

        pull_requests_pyd = [pr_orm_to_pydantic_short(pr_orm) for pr_orm in prs_orm]

        return {
            "user_id": user_id,
            "pull_requests": pull_requests_pyd
        }
