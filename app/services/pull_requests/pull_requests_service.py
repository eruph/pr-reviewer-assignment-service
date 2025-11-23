from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
from app.infrastructure.db.models import (
    PullRequestORM,
    UserORM,
    PullRequestStatus as ORMStatus
)
from app.domain.models import (
    PullRequest as PydanticPullRequest,
    ReassignResponse,
    pr_orm_to_pydantic,
    ErrorCode
)


class PullRequestService:
    def __init__(self, db: Session):
        self.db = db

    def create_pull_request(self, data: Dict[str, Any]) -> PydanticPullRequest:
        pull_request_id = data["pull_request_id"]
        pull_request_name = data["pull_request_name"]
        author_id = data["author_id"]

        existing_pr = self.db.query(PullRequestORM).filter(PullRequestORM.pull_request_id == pull_request_id).first()
        if existing_pr:
            raise ValueError(ErrorCode.PR_EXISTS)

        author_orm = self.db.query(UserORM).filter(UserORM.user_id == author_id).first()
        if not author_orm:
            raise ValueError(ErrorCode.NOT_FOUND)

        if not author_orm.team:
            raise ValueError(ErrorCode.NOT_FOUND)

        pr_orm = PullRequestORM(
            pull_request_id=pull_request_id,
            pull_request_name=pull_request_name,
            author=author_orm,
            status=ORMStatus.OPEN
        )
        self.db.add(pr_orm)
        self.db.flush()

        team_members = author_orm.team.members
        eligible_reviewers = [m for m in team_members if m.is_active and m.user_id != author_id]

        reviewers_to_assign = random.sample(eligible_reviewers, min(2, len(eligible_reviewers)))

        for reviewer in reviewers_to_assign:
            pr_orm.reviewers.append(reviewer)

        self.db.commit()
        self.db.refresh(pr_orm)

        return pr_orm_to_pydantic(pr_orm)

    def merge_pull_request(self, data: Dict[str, Any]) -> PydanticPullRequest:
        pull_request_id = data["pull_request_id"]

        pr_orm = self.db.query(PullRequestORM).filter(PullRequestORM.pull_request_id == pull_request_id).first()
        if not pr_orm:
            raise ValueError(ErrorCode.NOT_FOUND)

        if pr_orm.status == ORMStatus.MERGED:
            return pr_orm_to_pydantic(pr_orm)

        pr_orm.status = ORMStatus.MERGED
        pr_orm.merged_at = func.now()
        self.db.commit()
        self.db.refresh(pr_orm)

        return pr_orm_to_pydantic(pr_orm)

    def reassign_reviewer(self, data: Dict[str, Any]) -> ReassignResponse:
        pull_request_id = data["pull_request_id"]
        old_user_id = data["old_user_id"]

        pr_orm = self.db.query(PullRequestORM).filter(PullRequestORM.pull_request_id == pull_request_id).first()
        if not pr_orm:
            raise ValueError(ErrorCode.NOT_FOUND)

        if not pr_orm.can_modify_reviewers():
            raise ValueError(ErrorCode.PR_MERGED)

        old_reviewer_orm = self.db.query(UserORM).filter(UserORM.user_id == old_user_id).first()
        if not old_reviewer_orm:
            raise ValueError(ErrorCode.NOT_FOUND)

        if old_reviewer_orm not in pr_orm.reviewers:
            raise ValueError(ErrorCode.NOT_ASSIGNED)

        if not old_reviewer_orm.team:
            raise ValueError(ErrorCode.NO_CANDIDATE)

        team_members = old_reviewer_orm.team.members
        eligible_candidates = [
            m for m in team_members
            if m.is_active and m.user_id != old_user_id and m.user_id != pr_orm.author_id
        ]

        if not eligible_candidates:
            raise ValueError(ErrorCode.NO_CANDIDATE)

        new_reviewer_orm = random.choice(eligible_candidates)

        pr_orm.reviewers.remove(old_reviewer_orm)
        if new_reviewer_orm not in pr_orm.reviewers:
            pr_orm.reviewers.append(new_reviewer_orm)

        self.db.commit()
        self.db.refresh(pr_orm)
        pr_pyd = pr_orm_to_pydantic(pr_orm)
        return ReassignResponse(pr=pr_pyd, replaced_by=new_reviewer_orm.user_id)
