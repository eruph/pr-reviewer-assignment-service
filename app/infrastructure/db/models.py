from __future__ import annotations
from typing import List
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Table,
    Index,
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class PullRequestStatus(str, enum.Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


pull_request_reviewers = Table(
    "pull_request_reviewers",
    Base.metadata,
    Column("pr_id", String, ForeignKey("pull_requests.pull_request_id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", String, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True),
    Column("assigned_at", DateTime, default=datetime.utcnow, nullable=False),
    Index("ix_pr_reviewer_user_id", "user_id"),
)


class TeamORM(Base):
    __tablename__ = "teams"

    team_name = Column(String, primary_key=True, index=True)
    members = relationship("UserORM", back_populates="team", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"TeamORM(team_name={self.team_name})"


class UserORM(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    team_name = Column(String, ForeignKey("teams.team_name", ondelete="SET NULL"), nullable=True)
    team = relationship("TeamORM", back_populates="members", lazy="joined")

    authored_prs = relationship("PullRequestORM", back_populates="author", cascade="all, delete-orphan", lazy="selectin")

    reviewing_prs = relationship(
        "PullRequestORM",
        secondary=pull_request_reviewers,
        back_populates="reviewers",
        lazy="selectin",
    )

    def __repr__(self):
        return f"UserORM(user_id={self.user_id}, username={self.username}, is_active={self.is_active})"


class PullRequestORM(Base):
    __tablename__ = "pull_requests"

    pull_request_id = Column(String, primary_key=True, index=True)
    pull_request_name = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    author = relationship("UserORM", back_populates="authored_prs", lazy="joined")

    status = Column(Enum(PullRequestStatus), default=PullRequestStatus.OPEN, nullable=False)

    created_at = Column("createdAt", DateTime, default=datetime.utcnow, nullable=False)
    merged_at = Column("mergedAt", DateTime, nullable=True)

    reviewers = relationship(
        "UserORM",
        secondary=pull_request_reviewers,
        back_populates="reviewing_prs",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_pr_status", "status"),
    )

    def __repr__(self):
        return f"PullRequestORM(pr_id={self.pull_request_id}, status={self.status})"

    def assigned_reviewers_ids(self) -> List[str]:
        return [u.user_id for u in self.reviewers]

    def can_modify_reviewers(self) -> bool:
        return self.status == PullRequestStatus.OPEN
