from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.infrastructure.db.models import pull_request_reviewers

class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def get_reviewer_assignment_counts(self) -> Dict[str, int]:
        result = self.db.query(
            pull_request_reviewers.c.user_id,
            func.count(pull_request_reviewers.c.user_id).label('count')
        ).group_by(pull_request_reviewers.c.user_id).all()

        return {row.user_id: row.count for row in result}
