from typing import Optional, List
from sqlalchemy.orm import Session

from app.db_models import UserModel, PullRequestModel, PullRequestReviewerModel
from app.models import User, PullRequestShort


def _user_to_dto(user: UserModel) -> User:
    return User(
        user_id=user.user_id,
        username=user.username,
        team_name=user.team_name,
        is_active=user.is_active,
    )


def set_user_active(db: Session, user_id: str, is_active: bool) -> Optional[User]:
    user = db.query(UserModel).filter_by(user_id=user_id).first()
    if not user:
        return None

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return _user_to_dto(user)


def get_user_reviews(db: Session, user_id: str) -> List[PullRequestShort]:
    prs = (
        db.query(PullRequestModel)
        .join(
            PullRequestReviewerModel,
            PullRequestReviewerModel.pull_request_id
            == PullRequestModel.pull_request_id,
        )
        .filter(PullRequestReviewerModel.reviewer_id == user_id)
        .all()
    )

    return [
        PullRequestShort(
            pull_request_id=pr.pull_request_id,
            pull_request_name=pr.pull_request_name,
            author_id=pr.author_id,
            status=pr.status,
        )
        for pr in prs
    ]
