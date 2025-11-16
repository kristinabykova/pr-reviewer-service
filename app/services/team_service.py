from typing import Optional
from sqlalchemy.orm import Session

from app.db_models import TeamModel, UserModel
from app.models import Team, TeamMember


def _user_to_member_dto(user: UserModel) -> TeamMember:
    return TeamMember(
        user_id=user.user_id,
        username=user.username,
        is_active=user.is_active,
    )


def _team_to_dto(team: TeamModel, users: list[UserModel]) -> Team:
    return Team(
        team_name=team.team_name,
        members=[_user_to_member_dto(u) for u in users],
    )


def create_team(db: Session, team_data: Team) -> Optional[Team]:
    existing = db.query(TeamModel).filter_by(team_name=team_data.team_name).first()
    if existing:
        return None

    team = TeamModel(team_name=team_data.team_name)
    db.add(team)

    for member in team_data.members:
        user = db.query(UserModel).filter_by(user_id=member.user_id).first()
        if user:
            user.username = member.username
            user.team_name = team_data.team_name
            user.is_active = member.is_active
        else:
            db.add(
                UserModel(
                    user_id=member.user_id,
                    username=member.username,
                    team_name=team_data.team_name,
                    is_active=member.is_active,
                )
            )

    db.commit()

    users = (
        db.query(UserModel)
        .filter(UserModel.team_name == team_data.team_name)
        .order_by(UserModel.user_id)
        .all()
    )

    return _team_to_dto(team, users)


def get_team(db: Session, team_name: str) -> Optional[Team]:
    team = db.query(TeamModel).filter_by(team_name=team_name).first()
    if not team:
        return None

    users = (
        db.query(UserModel)
        .filter(UserModel.team_name == team_name)
        .order_by(UserModel.user_id)
        .all()
    )

    return _team_to_dto(team, users)
