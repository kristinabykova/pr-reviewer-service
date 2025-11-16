# app/routers/teams.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Team, TeamResponse, ErrorResponse
from app.services import team_service

router = APIRouter(prefix="/team", tags=["Teams"])


@router.post(
    "/add",
    summary="Создать команду с участниками (создаёт/обновляет пользователей)",
    status_code=status.HTTP_201_CREATED,
    response_model=TeamResponse,
    responses={
        201: {
            "description": "Команда создана",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "team": {"$ref": "#/components/schemas/Team"}
                        },
                    },
                    "example": {
                        "team": {
                            "team_name": "backend",
                            "members": [
                                {
                                    "user_id": "u1",
                                    "username": "Alice",
                                    "is_active": True,
                                },
                                {
                                    "user_id": "u2",
                                    "username": "Bob",
                                    "is_active": True,
                                },
                            ],
                        }
                    },
                }
            },
        },
        400: {
            "description": "Команда уже существует",
            "model" : ErrorResponse,
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "error": {
                            "code": "TEAM_EXISTS",
                            "message": "team_name already exists",
                        }
                    },
                }
            },
        },
    },
)
def add_team(team: Team, db: Session = Depends(get_db)):
    created = team_service.create_team(db, team)
    if created is None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "TEAM_EXISTS",
                    "message": "team_name already exists",
                }
            },
        )
    return {"team": created}


@router.get(
    "/get",
    summary="Получить команду с участниками",
    response_model=Team,
    responses={
        200: {
            "description": "Объект команды",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Team"},
                    "example": {
                        "team_name": "backend",
                        "members": [
                            {
                                "user_id": "u1",
                                "username": "Alice",
                                "is_active": True,
                            },
                            {
                                "user_id": "u2",
                                "username": "Bob",
                                "is_active": True,
                            },
                        ],
                    },
                }
            },
        },
        404: {
            "description": "Команда не найдена",
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
def get_team(team_name: str = Query(...), db: Session = Depends(get_db)):
    team = team_service.get_team(db, team_name)
    if team is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "resource not found",
                }
            },
        )
    return team
