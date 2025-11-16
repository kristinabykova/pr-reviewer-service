from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ErrorInfo(BaseModel):
    code: Literal["TEAM_EXISTS", "PR_EXISTS", "PR_MERGED", "NOT_ASSIGNED", "NO_CANDIDATE", "NOT_FOUND"]
    message: str


class ErrorInfo(BaseModel):
    code: Literal[
        "TEAM_EXISTS",
        "PR_EXISTS",
        "PR_MERGED",
        "NOT_ASSIGNED",
        "NO_CANDIDATE",
        "NOT_FOUND",
    ]
    message: str

class ErrorResponse(BaseModel):
    error: ErrorInfo

class TeamMember(BaseModel):
    user_id: str
    username: str
    is_active: bool = Field(alias="is_active")


class Team(BaseModel):
    team_name: str
    members: List[TeamMember]

class TeamResponse(BaseModel):
    team: Team

class User(BaseModel):
    user_id: str
    username: str
    team_name: str
    is_active: bool

class UserResponse(BaseModel):
    user: User

class PullRequest(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: Literal["OPEN", "MERGED"]
    assigned_reviewers: List[str]
    createdAt: Optional[datetime] = None
    mergedAt: Optional[datetime] = None


class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: Literal["OPEN", "MERGED"]


class SetUserActiveRequest(BaseModel):
    user_id: str
    is_active: bool


class CreatePRRequest(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class MergePRRequest(BaseModel):
    pull_request_id: str


class ReassignPRRequest(BaseModel):
    pull_request_id: str
    old_user_id: str = Field(alias="old_user_id")

class UserReviewsResponse(BaseModel):
    user_id: str
    pull_requests: List[PullRequestShort]

class PRResponse(BaseModel):
    pr: PullRequest

class PRReassignResponse(BaseModel):
    pr: PullRequest
    replaced_by: str