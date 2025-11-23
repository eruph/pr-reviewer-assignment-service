from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.infrastructure.db.models import TeamORM, UserORM
from app.domain.models import (
    Team as PydanticTeam,
    TeamMember,
    ErrorCode
)


class TeamService:
    def __init__(self, db: Session):
        self.db = db

    def add_team(self, pydantic_team: PydanticTeam) -> PydanticTeam:
        existing_team = self.db.query(TeamORM).filter(TeamORM.team_name == pydantic_team.team_name).first()
        if existing_team:
            raise ValueError(ErrorCode.TEAM_EXISTS)

        team_orm = TeamORM(team_name=pydantic_team.team_name)
        self.db.add(team_orm)

        for member in pydantic_team.members:
            user_orm = UserORM(
                user_id=member.user_id,
                username=member.username,
                is_active=member.is_active,
                team=team_orm
            )
            self.db.add(user_orm)

        try:
            self.db.commit()
            self.db.refresh(team_orm)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("DATABASE_ERROR")

        members_pyd = [
            TeamMember(user_id=m.user_id, username=m.username, is_active=m.is_active)
            for m in team_orm.members
        ]
        return PydanticTeam(team_name=team_orm.team_name, members=members_pyd)

    def get_team(self, team_name: str) -> PydanticTeam:
        team_orm = self.db.query(TeamORM).filter(TeamORM.team_name == team_name).first()
        if not team_orm:
            raise ValueError(ErrorCode.NOT_FOUND)

        members_pyd = [
            TeamMember(user_id=m.user_id, username=m.username, is_active=m.is_active)
            for m in team_orm.members
        ]
        return PydanticTeam(team_name=team_orm.team_name, members=members_pyd)
