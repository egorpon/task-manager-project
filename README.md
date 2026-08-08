# Task Manager API

A REST API for managing projects, tasks, and comments with team assignment, file attachments, and email notifications — built with Django REST Framework.

```
Client -> Django REST Framework (:8000) -> PostgreSQL (:5432)
                                         -> Celery worker -> RabbitMQ (:5672)
```

## Features

- **Projects** — owned by a user, with a due date and nested tasks
- **Tasks** — assigned to multiple users (via `AssignedUser`), with priority/status, due dates, and file attachments
- **Comments** — posted on tasks by assigned users or the project owner
- **Access control** — project owners and assigned users see only what's relevant to them; staff see everything
- **Async email notifications** — assigning a task emails everyone assigned, via Celery
- **File attachments** — upload files to a task, list and delete them
- **JWT authentication** via `djangorestframework-simplejwt`
- **OpenAPI schema** — interactive docs via `drf-spectacular` (Swagger UI + Redoc)
- **Filtering & search** — filter projects/tasks by name, due date, or task count; search by name
- **Request profiling** via `django-silk`

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0, Django REST Framework |
| Database | PostgreSQL |
| Auth | JWT (`simplejwt`) |
| Async tasks | Celery + RabbitMQ |
| API docs | drf-spectacular (OpenAPI 3) |
| Filtering | django-filter |
| Profiling | django-silk |
| Dependency management | uv |
| Containerization | Docker, Docker Compose |

## Project Structure

```
mt_project/            # Django settings, root URLs, Celery app entrypoint
project/                # Project model + admin
task/                    # Task, AssignedUser, AttachedFiles models + admin
comment/                  # Comment model + admin
api/
├── permissions.py         # IsAdminOrProjectOwner
├── task.py                # Celery task: send_assigned_task_email
├── projects/
│   ├── views.py, serializers.py, filters.py, urls.py, tests.py
├── tasks/
│   ├── views.py, serializers.py, filters.py, urls.py, tests.py
└── comments/
    ├── views.py, serializers.py, filters.py, urls.py, tests.py
utils/
└── random_due_date.py      # Helper for generating sample due dates
```

Each domain (`projects`, `tasks`, `comments`) is self-contained under `api/`, with its own views, serializers, filters, and tests.

## Data Model

- **Project** — `name`, `description`, `owner` (FK to User), `due_date`
- **Task** — belongs to a `Project`, has `priority`/`status` choices, `due_date`, and a many-to-many to `User` through `AssignedUser`
- **AssignedUser** — join table between `Task` and `User`, with `assigned_at`
- **AttachedFiles** — files uploaded to a `Task`
- **Comment** — belongs to a `Task`, posted by a `User`

## Access Rules

| Who | Can see |
|---|---|
| Staff (`is_staff`) | Everything |
| Project owner | Their own projects and all tasks/comments within them |
| Assigned user | Tasks they're assigned to, and comments on those tasks |
| Everyone else | Nothing for that resource |

Task creation is validated so a task can only be assigned to a project the requesting user owns (or any project, if staff). Task due dates can't be later than the parent project's due date.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Obtain JWT access/refresh pair |
| POST | `/api/token/refresh/` | Refresh access token |
| GET | `/projects/` | List projects (filter/search/order) |
| POST | `/projects/create/` | Create a project |
| GET | `/projects/<project_id>/` | Retrieve a project with its tasks |
| PUT/PATCH | `/projects/<project_id>/update/` | Update a project |
| DELETE | `/projects/<project_id>/delete/` | Delete a project |
| GET | `/tasks/` | List tasks (filter/search/order) |
| POST | `/tasks/create/` | Create a task (sends assignment emails) |
| GET | `/tasks/<task_id>/` | Retrieve a task |
| PUT/PATCH | `/tasks/<task_id>/update/` | Update a task |
| DELETE | `/tasks/<task_id>/delete/` | Delete a task |
| GET | `/tasks/<task_id>/comments/` | List comments on a task |
| GET | `/tasks/<task_id>/attachments/` | List a task's attachments |
| DELETE | `/tasks/<task_id>/attachments/<file_id>/delete/` | Delete an attachment |
| GET | `/comments/` | List comments (filter/order) |
| POST | `/comments/create/` | Add a comment |
| GET | `/comments/<comment_id>/` | Retrieve a comment |
| PUT/PATCH | `/comments/<comment_id>/update/` | Update a comment |
| DELETE | `/comments/<comment_id>/delete/` | Delete a comment |
| GET | `/api/schema/swagger-ui/` | Interactive API docs |
| GET | `/api/schema/redoc/` | Redoc API docs |

Filtering examples:

```
GET /projects/?total_tasks__gt=3
GET /projects/?due_date__gt=2026-01-01
GET /tasks/?search=homepage
```

## Getting Started

### Prerequisites

- Docker + Docker Compose

### Setup

1. Create a `.env` file in the project root:

   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DEBUG=1
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

   POSTGRES_NAME=tm_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=admin
   POSTGRES_HOST=postgres_db
   POSTGRES_PORT=5432

   CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
   CELERY_RESULT_BACKEND=rpc://guest:guest@rabbitmq:5672//
   ```

   > Note: `POSTGRES_HOST`/broker URLs above use Docker service names — they only resolve when Django itself runs inside Docker. Running `manage.py` on the host instead requires `POSTGRES_HOST=localhost` and matching broker URLs.

2. Start everything:

   ```bash
   docker-compose up --build
   ```

   This starts PostgreSQL, RabbitMQ, the API (migrating on boot), the Celery worker, and Adminer.

Open `http://localhost:8000`.

### Running locally with uv (without Docker)

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Requires PostgreSQL and RabbitMQ reachable at `localhost` — adjust `.env` accordingly.

## Running

| Service | URL |
|---|---|
| API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/api/schema/swagger-ui/` |
| Redoc | `http://localhost:8000/api/schema/redoc/` |
| Django admin | `http://localhost:8000/admin/` |
| Request profiler (silk) | `http://localhost:8000/silk/` |
| Adminer (DB UI) | `http://localhost:8888` |
| RabbitMQ management | `http://localhost:15672` |

## Development

```bash
docker-compose exec api python manage.py test        # run tests
docker-compose exec api python manage.py shell       # Django shell
docker-compose logs -f celery                          # watch worker logs
```