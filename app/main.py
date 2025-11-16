from fastapi import FastAPI

from app.routers import teams, users, pull_requests, health

app = FastAPI(
    title="PR Reviewer Assignment Service (Test Task, Fall 2025)",
    version="1.0.0",
)

app.include_router(teams.router)
app.include_router(users.router)
app.include_router(pull_requests.router)
app.include_router(health.router)