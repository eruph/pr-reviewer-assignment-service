from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from app.infrastructure.db.models import UserORM, PullRequestORM, PullRequestStatus as ORMStatus

class ErrorCode(str, Enum):
    TEAM_EXISTS = "TEAM_EXISTS"
    PR_EXISTS = "PR_EXISTS"
    PR_MERGED = "PR_MERGED"
    NOT_ASSIGNED = "NOT_ASSIGNED"
    NO_CANDIDATE = "NO_CANDIDATE"
    NOT_FOUND = "NOT_FOUND"

class PullRequestStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"

class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail

class TeamMember(BaseModel):
    user_id: str
    username: str
    is_active: bool

class Team(BaseModel):
    team_name: str
    members: List[TeamMember]

class User(BaseModel):
    user_id: str
    username: str
    team_name: str
    is_active: bool

class PullRequest(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PullRequestStatus
    assigned_reviewers: List[str]
    createdAt: Optional[datetime] = None
    mergedAt: Optional[datetime] = None

class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PullRequestStatus

class ReassignResponse(BaseModel):
    pr: PullRequest
    replaced_by: str

def user_orm_to_pydantic(user_orm: UserORM) -> User:
    return User(
        user_id=user_orm.user_id,
        username=user_orm.username,
        team_name=user_orm.team_name,
        is_active=user_orm.is_active
    )

def pr_orm_to_pydantic(pr_orm: PullRequestORM) -> PullRequest:
    return PullRequest(
        pull_request_id=pr_orm.pull_request_id,
        pull_request_name=pr_orm.pull_request_name,
        author_id=pr_orm.author_id,
        status=PullRequestStatus(pr_orm.status.value),
        assigned_reviewers=pr_orm.assigned_reviewers_ids(),
        createdAt=pr_orm.created_at,
        mergedAt=pr_orm.merged_at
    )

def pr_orm_to_pydantic_short(pr_orm: PullRequestORM) -> PullRequestShort:
    return PullRequestShort(
        pull_request_id=pr_orm.pull_request_id,
        pull_request_name=pr_orm.pull_request_name,
        author_id=pr_orm.author_id,
        status=PullRequestStatus(pr_orm.status.value)
    )


# статистика

class StatsResponse(BaseModel):
    reviewer_assignment_counts: Dict[str, int]