from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (
    CreatePRRequest,
    MergePRRequest,
    ReassignPRRequest,
    PRResponse,
    PRReassignResponse,
)
from app.services import pr_service

router = APIRouter(prefix="/pullRequest", tags=["PullRequests"])


@router.post(
    "/create",
    summary = "Создать PR и автоматически назначить до 2 ревьюверов из команды автора",
    status_code=status.HTTP_201_CREATED,
    response_model=PRResponse,
    responses={
        201: {
            "description": "PR создан",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"pr": {"$ref": "#/components/schemas/PullRequest"}},
                    },
                    "example": {
                        "pr": {
                            "pull_request_id": "pr-1001",
                            "pull_request_name": "Add search",
                            "author_id": "u1",
                            "status": "OPEN",
                            "assigned_reviewers": ["u2", "u3"],
                        }
                    },
                }
            },
        },
        404: {
            "description": "Автор/команда не найдены",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                }
            },
        },
        409: {
            "description": "PR уже существует",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "error": {
                            "code": "PR_EXISTS",
                            "message": "PR id already exists",
                        }
                    },
                }
            },
        },
    },
)
def create_pr(body: CreatePRRequest, db: Session = Depends(get_db)):
    status_code, pr = pr_service.create_pr(
        db,
        pr_id=body.pull_request_id,
        name=body.pull_request_name,
        author_id=body.author_id,
    )

    if status_code == "pr_exists":
        raise HTTPException(
            status_code=409,
            detail={
                "error": {"code": "PR_EXISTS", "message": "PR id already exists"}
            },
        )

    if status_code in ("author_not_found", "team_not_found"):
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "resource not found",
                }
            },
        )

    return {"pr": pr}


@router.post(
    "/merge",
    summary = "Пометить PR как MERGED (идемпотентная операция)",
    response_model=PRResponse,
    responses={
        200: {
            "description": "PR в состоянии MERGED",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"pr": {"$ref": "#/components/schemas/PullRequest"}},
                    },
                    "example": {
                        "pr": {
                            "pull_request_id": "pr-1001",
                            "pull_request_name": "Add search",
                            "author_id": "u1",
                            "status": "MERGED",
                            "assigned_reviewers": ["u2", "u3"],
                            "mergedAt": "2025-10-24T12:34:56Z",
                        }
                    },
                }
            },
        },
        404: {
            "description": "PR не найден",
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
def merge_pr(body: MergePRRequest, db: Session = Depends(get_db)):
    status_code, pr = pr_service.merge_pr(db, body.pull_request_id)
    if status_code == "not_found":
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "resource not found"}},
        )
    return {"pr": pr}


@router.post(
    "/reassign",
    summary = "Переназначить конкретного ревьювера на другого из его команды",
    response_model=PRReassignResponse,
    responses={
        200: {
            "description": "Переназначение выполнено",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["pr", "replaced_by"],
                        "properties": {
                            "pr": {"$ref": "#/components/schemas/PullRequest"},
                            "replaced_by": {
                                "type": "string",
                                "description": "user_id нового ревьювера",
                            },
                        },
                    },
                    "example": {
                        "pr": {
                            "pull_request_id": "pr-1001",
                            "pull_request_name": "Add search",
                            "author_id": "u1",
                            "status": "OPEN",
                            "assigned_reviewers": ["u3", "u5"],
                        },
                        "replaced_by": "u5",
                    },
                }
            },
        },
        404: {
            "description": "PR или пользователь не найден",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                }
            },
        },
        409: {
            "description": "Нарушение доменных правил переназначения",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "examples": {
                        "merged": {
                            "summary": "Нельзя менять после MERGED",
                            "value": {
                                "error": {
                                    "code": "PR_MERGED",
                                    "message": "cannot reassign on merged PR",
                                }
                            },
                        },
                        "notAssigned": {
                            "summary": "Пользователь не был назначен ревьювером",
                            "value": {
                                "error": {
                                    "code": "NOT_ASSIGNED",
                                    "message": "reviewer is not assigned to this PR",
                                }
                            },
                        },
                        "noCandidate": {
                            "summary": "Нет доступных кандидатов",
                            "value": {
                                "error": {
                                    "code": "NO_CANDIDATE",
                                    "message": "no active replacement candidate in team",
                                }
                            },
                        },
                    },
                }
            },
        },
    },
)
def reassign_pr(body: ReassignPRRequest, db: Session = Depends(get_db)):
    status_code, pr, replaced_by = pr_service.reassign_reviewer(
        db, body.pull_request_id, body.old_user_id
    )

    if status_code in ("pr_not_found", "user_not_found"):
        raise HTTPException(
            status_code=404,
            detail={
                "error": {"code": "NOT_FOUND", "message": "resource not found"}
            },
        )

    if status_code == "merged":
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "PR_MERGED",
                    "message": "cannot reassign on merged PR",
                }
            },
        )

    if status_code == "not_assigned":
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "NOT_ASSIGNED",
                    "message": "reviewer is not assigned to this PR",
                }
            },
        )

    if status_code == "no_candidate":
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "NO_CANDIDATE",
                    "message": "no active replacement candidate in team",
                }
            },
        )

    return {"pr": pr, "replaced_by": replaced_by}
