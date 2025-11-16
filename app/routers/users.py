from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (
    SetUserActiveRequest,
    UserResponse,
    UserReviewsResponse,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/setIsActive",
    summary = "Установить флаг активности пользователя",
    response_model=UserResponse,
    responses={
        200: {
            "description": "Обновлённый пользователь",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "user": {"$ref": "#/components/schemas/User"}
                        },
                    },
                    "example": {
                        "user": {
                            "user_id": "u2",
                            "username": "Bob",
                            "team_name": "backend",
                            "is_active": False,
                        }
                    },
                }
            },
        },
        404: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                }
            },
        },
    },
)
def set_is_active(body: SetUserActiveRequest, db: Session = Depends(get_db)):
    user = user_service.set_user_active(db, body.user_id, body.is_active)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "resource not found",
                }
            },
        )
    return {"user": user}


@router.get(
    "/getReview",
    summary = "Получить PR'ы, где пользователь назначен ревьювером",
    response_model=UserReviewsResponse,
    responses={
        200: {
            "description": "Список PR'ов пользователя",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["user_id", "pull_requests"],
                        "properties": {
                            "user_id": {"type": "string"},
                            "pull_requests": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/PullRequestShort"
                                },
                            },
                        },
                    },
                    "example": {
                        "user_id": "u2",
                        "pull_requests": [
                            {
                                "pull_request_id": "pr-1001",
                                "pull_request_name": "Add search",
                                "author_id": "u1",
                                "status": "OPEN",
                            }
                        ],
                    },
                }
            },
        }
    },
)
def get_review(user_id: str = Query(...), db: Session = Depends(get_db)):
    prs = user_service.get_user_reviews(db, user_id)
    return {"user_id": user_id, "pull_requests": prs}
