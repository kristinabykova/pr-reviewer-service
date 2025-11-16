from typing import Optional, Tuple, List
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db_models import (
    PullRequestModel,
    PullRequestReviewerModel,
    UserModel,
)
from app.models import PullRequest


def _pr_to_dto(pr: PullRequestModel, reviewers: List[str]) -> PullRequest:
    return PullRequest(
        pull_request_id=pr.pull_request_id,
        pull_request_name=pr.pull_request_name,
        author_id=pr.author_id,
        status=pr.status,
        assigned_reviewers=reviewers,
        createdAt=pr.created_at,
        mergedAt=pr.merged_at,
    )


def _get_reviewers_ids(db: Session, pr_id: str) -> List[str]:
    rows = (
        db.query(PullRequestReviewerModel.reviewer_id)
        .filter(PullRequestReviewerModel.pull_request_id == pr_id)
        .all()
    )
    return [r[0] for r in rows]


def create_pr(
    db: Session, pr_id: str, name: str, author_id: str
) -> Tuple[str, Optional[PullRequest]]:
    """
    Возвращает кортеж (status, pr):
      status:
        - "ok"
        - "pr_exists"
        - "author_not_found"
        - "team_not_found"
    """
    existing = (
        db.query(PullRequestModel).filter_by(pull_request_id=pr_id).first()
    )
    if existing:
        return "pr_exists", None

    author = db.query(UserModel).filter_by(user_id=author_id).first()
    if not author:
        return "author_not_found", None

    if not author.team_name:
        return "team_not_found", None

    candidates_q = (
        db.query(UserModel.user_id)
        .filter(
            UserModel.team_name == author.team_name,
            UserModel.is_active == True,
            UserModel.user_id != author_id,
        )
        .order_by(func.random())
        .limit(2)
    )
    candidates = [row[0] for row in candidates_q.all()]

    pr = PullRequestModel(
        pull_request_id=pr_id,
        pull_request_name=name,
        author_id=author_id,
        status="OPEN",
        created_at=datetime.now(timezone.utc), 
    )
    db.add(pr)
    db.flush()

    for c in candidates:
        db.add(
            PullRequestReviewerModel(
                pull_request_id=pr_id,
                reviewer_id=c,
            )
        )

    db.commit()
    db.refresh(pr)

    reviewers = _get_reviewers_ids(db, pr_id)
    return "ok", _pr_to_dto(pr, reviewers)


def merge_pr(db: Session, pr_id: str) -> Tuple[str, Optional[PullRequest]]:
    pr = db.query(PullRequestModel).filter_by(pull_request_id=pr_id).first()
    if not pr:
        return "not_found", None

    if pr.status != "MERGED":
        pr.status = "MERGED"
        pr.merged_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(pr)

    reviewers = _get_reviewers_ids(db, pr_id)
    return "ok", _pr_to_dto(pr, reviewers)


def reassign_reviewer(
    db: Session, pr_id: str, old_user_id: str
) -> Tuple[str, Optional[PullRequest], Optional[str]]:
    pr = db.query(PullRequestModel).filter_by(pull_request_id=pr_id).first()
    if not pr:
        return "pr_not_found", None, None

    user = db.query(UserModel).filter_by(user_id=old_user_id).first()
    if not user:
        return "user_not_found", None, None

    if pr.status == "MERGED":
        return "merged", None, None

    rows = (
        db.query(PullRequestReviewerModel)
        .filter(PullRequestReviewerModel.pull_request_id == pr_id)
        .all()
    )
    reviewer_ids = {r.reviewer_id for r in rows}

    if old_user_id not in reviewer_ids:
        return "not_assigned", None, None

    candidates_q = (
        db.query(UserModel.user_id)
        .filter(
            UserModel.team_name == user.team_name,
            UserModel.is_active == True,
            UserModel.user_id != old_user_id,
            ~UserModel.user_id.in_(reviewer_ids),
        )
        .order_by(func.random())
        .limit(1)
    )
    row = candidates_q.first()
    if not row:
        return "no_candidate", None, None

    new_user_id = row[0]

    (
        db.query(PullRequestReviewerModel)
        .filter(
            PullRequestReviewerModel.pull_request_id == pr_id,
            PullRequestReviewerModel.reviewer_id == old_user_id,
        )
        .update({"reviewer_id": new_user_id})
    )

    db.commit()
    db.refresh(pr)

    reviewers = _get_reviewers_ids(db, pr_id)
    return "ok", _pr_to_dto(pr, reviewers), new_user_id


def get_pr_by_id(db: Session, pr_id: str) -> Optional[PullRequest]:
    pr = db.query(PullRequestModel).filter_by(pull_request_id=pr_id).first()
    if not pr:
        return None
    reviewers = _get_reviewers_ids(db, pr_id)
    return _pr_to_dto(pr, reviewers)
