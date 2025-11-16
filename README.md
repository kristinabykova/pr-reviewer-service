# PR Reviewer Assignment Service

Сервис для управления командами, пользователями и назначения ревьюверов к pull-request'ам.
Реализован на FastAPI + PostgreSQL, полностью соответствует предоставленному OpenAPI.

## Запуск проекта в Docker
1. Клонировать репозиторий

```
git clone https://github.com/kristinabykova/pr-reviewer-service.git
cd pr-reviewer-service
```

2. Собрать и запустить сервис

```
docker compose up --build
```

либо

```
make docker-up
```

Сервис доступен по адресу:

- Swagger UI → http://localhost:8080/docs  
- Health-check → http://localhost:8080/health  

## Технологический стек

Python 3.11\
FastAPI\
PostgreSQL 16\
SQLAlchemy\
Docker + Docker Compose\
Uvicorn

## Структура проекта
pr-reviewer-service/\
│\
├── app/\
│   ├── routers/        
│   ├── services/      
│   ├── db_models.py    
│   ├── models.py        
│   ├── db.py          
│   └── main.py         
│\
├── schema.sql  
├── Makefile\
├── requirements.txt\
├── docker-compose.yml\
├── Dockerfile\
├── requirements.txt\
└── README.md

## База данных

При первом запуске PostgreSQL автоматически инициализируется с помощью:

```
schema.sql
```

В составе:

* таблицы команд, пользователей, PR
* связи и внешние ключи
* индексирование
* таблица pull_request_reviewers

## Основные эндпоинты API

### Teams

POST /team/add — создать команду

GET /team/get — получить команду

### Users

POST /users/setIsActive — изменить активность пользователя

GET /users/getReview — получить PR, где пользователь ревьювер

### Pull Requests

POST /pullRequest/create — создать PR

POST /pullRequest/reassign — переназначить ревьювера

POST /pullRequest/merge — выполнить merge (идемпотентно)

### Health

GET /health — проверка состояния сервиса

**Документация доступна в Swagger UI.**


## Вопросы / Проблемы и логика их решений
1. Отсутствие health-метода в OpenAPI

В спецификации присутствовал тег Health, но не было описано ни одного метода.
Для удобства проверки и мониторинга был реализован простой endpoint:

```
GET /health → {"status": "ok"}
```
