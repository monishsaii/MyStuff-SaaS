# MyStuff SaaS

A multi-tenant SaaS backend built with **Django, PostgreSQL, and Docker Compose**. MyStuff is designed to support multiple organizations, with membership-based roles and organization-scoped access control.

The project focuses on backend fundamentals such as relational data modeling, authorization, database integrity, and automated testing.

## Tech Stack

- **Language:** Python
- **Backend:** Django
- **Database:** PostgreSQL
- **Database environment:** Docker Compose
- **Database driver:** Psycopg
- **Testing:** Django TestCase

## Core Features

### Custom User Model

- Custom Django user model with username, email, first name, and last name.
- Password hashing through Django's password-management utilities.
- Unique username and email fields.

### Organization Management

- Organization model for representing separate tenants.
- Organization-scoped memberships, allowing a user to belong to different organizations.
- Membership relationships between users and organizations.

### Role-Based Memberships

Membership roles:

- `OWNER`
- `ADMIN`
- `MANAGER`
- `MEMBER`

Membership statuses:

- `INVITED`
- `ACTIVE`
- `REMOVED`

The membership service implements invitation rules, including role-based restrictions and re-invitation of removed members.

### Database Integrity

- Unique constraint preventing duplicate membership records for the same user and organization.
- Database check constraints restricting membership roles and statuses to supported values.
- Foreign keys enforcing relationships between users, organizations, and inviters.
- Protected deletion behavior for related user and organization records.

### Automated Tests

The membership test suite has **21 passing tests** in the latest recorded run. These cover invitation permissions, membership status, re-invitation behavior, duplicate invitations, and organization isolation.

## Architecture

The application is organized into Django apps:

| App | Responsibility |
|---|---|
| `accounts` | Custom user model and account-related endpoints |
| `organizations` | Organization data model |
| `memberships` | Membership model, invitation service, roles, and permissions |
| `api` | API routing and endpoint logic |
| `config` | Django project settings and root URL configuration |

## Getting Started

### Prerequisites

- Python compatible with the installed Django version
- Docker Desktop with Docker Compose
- Git

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd "MyStuff SaaS"
```

Replace `<your-repository-url>` with the repository URL.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the project's required packages, including Django, Psycopg, and `python-dotenv`.

If a `requirements.txt` file is included in the repository, install the pinned dependencies with:

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root. Configure the Django secret key and PostgreSQL connection settings using the variable names expected by `config/settings.py`.

Docker Compose also expects these PostgreSQL variables:

```dotenv
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_local_password
```

Use consistent database credentials in Django and Docker Compose. Keep `.env` out of version control and never commit real secrets.

### 5. Start PostgreSQL

```powershell
docker compose up -d db
```

Wait for the database to become ready before proceeding.

### 6. Apply migrations

```powershell
python manage.py migrate
```

### 7. Run the development server

```powershell
python manage.py runserver
```

The local development server is available at `http://127.0.0.1:8000/`.

### 8. Run tests

Run the membership tests with:

```powershell
python manage.py test memberships
```

Run the full Django test suite with:

```powershell
python manage.py test
```

## Design Decisions

### Organization-scoped membership

A user's role belongs to their membership in a specific organization rather than being a single global role. This allows the same user to have different access levels across organizations.

### Database constraints as a second layer of protection

Application-level checks implement business rules, while database constraints protect membership uniqueness and valid role/status values.

### Invitation lifecycle

Membership records use explicit statuses to represent invitations, active membership, and removal. Re-inviting a removed member reuses the existing membership record rather than creating a duplicate.

## Current Scope and Limitations

MyStuff is an ongoing backend learning and portfolio project.

- The membership invitation and authorization logic has automated test coverage.
- The project uses PostgreSQL and Docker Compose for local development.
- End-to-end authentication, invitation acceptance, complete project CRUD, production deployment, and a frontend should be considered incomplete until implemented and verified.
- Advanced concurrent invitation handling and production hardening remain areas for further development.

## Future Improvements

- Complete and test end-to-end authentication and invitation acceptance.
- Implement project CRUD with organization-level authorization.
- Improve transaction handling for concurrent membership operations.
- Add API validation and consistent error responses.
- Add production configuration, deployment, logging, and security hardening.

## Author

Built as a backend engineering portfolio project to explore Django, PostgreSQL, multi-tenant application design, and authorization.
