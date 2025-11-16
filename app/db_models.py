from sqlalchemy import (
    Column,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TeamModel(Base):
    __tablename__ = "teams"

    team_name = Column(Text, primary_key=True)

    members = relationship("UserModel", back_populates="team")


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Text, primary_key=True)
    username = Column(Text, nullable=False)
    team_name = Column(Text, ForeignKey("teams.team_name"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    team = relationship("TeamModel", back_populates="members")
    authored_prs = relationship("PullRequestModel", back_populates="author")
    review_prs = relationship("PullRequestReviewerModel", back_populates="reviewer")


class PullRequestModel(Base):
    __tablename__ = "pull_requests"

    pull_request_id = Column(Text, primary_key=True)
    pull_request_name = Column(Text, nullable=False)
    author_id = Column(Text, ForeignKey("users.user_id"), nullable=False)
    status = Column(Text, nullable=False)  # OPEN | MERGED
    created_at = Column(DateTime(timezone=True))
    merged_at = Column(DateTime(timezone=True))

    author = relationship("UserModel", back_populates="authored_prs")
    reviewers = relationship(
        "PullRequestReviewerModel",
        back_populates="pull_request",
        cascade="all, delete-orphan",
    )


class PullRequestReviewerModel(Base):
    __tablename__ = "pull_request_reviewers"

    pull_request_id = Column(
        Text, ForeignKey("pull_requests.pull_request_id"), primary_key=True
    )
    reviewer_id = Column(Text, ForeignKey("users.user_id"), primary_key=True)

    pull_request = relationship("PullRequestModel", back_populates="reviewers")
    reviewer = relationship("UserModel", back_populates="review_prs")
