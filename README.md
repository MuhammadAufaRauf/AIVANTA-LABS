# Aivanta OS

**Aivanta Labs** · Intelligence. Innovation. Automation.

A local-first virtual company management system. Phase 1 provides the Next.js dashboard foundation, FastAPI service, SQLite company configuration, and health checks. Phase 2 adds database-backed department, AI employee, task, and project management. AI execution and 9Router integration are intentionally not included yet.

## Requirements

- Node.js 20+ and npm
- Python 3.12
- Windows PowerShell (commands below), Windows Terminal, or another shell

## Run locally on Windows

Open two PowerShell terminals in the repository root.

### 1. Backend API

```powershell
cd backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

On first startup, the API preserves the existing SQLite database, adds any missing Phase 1 configuration columns without dropping data, creates the new workforce tables, and seeds the eight departments and four initial employees idempotently.

- API docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/api/v1/health>
- Company: <http://localhost:8000/api/v1/company>

### 2. Frontend

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open <http://localhost:3000>. Employee, department, task, project, and overview data are fetched from the backend API; there are no frontend sample records.

## Workforce API

All paths use `/api/v1`.

| Resource | Endpoints |
|---|---|
| Dashboard | `GET /dashboard/stats` |
| Departments | `GET, POST /departments`; `GET, PATCH, DELETE /departments/{id}`; `GET /departments/{id}/employees` |
| Employees | `GET, POST /employees`; `GET, PATCH, DELETE /employees/{id}` |
| Tasks | `GET, POST /tasks`; `GET, PATCH, DELETE /tasks/{id}` |
| Projects | `GET, POST /projects`; `GET, PATCH, DELETE /projects/{id}` |

Filtering: employees accept `department_id`, `status`, `search`; tasks accept `status`, `priority`, `employee_id`, `project_id`, `search`; projects accept `status`, `priority`, `search`.

Deleting a department with employees or a project with tasks is rejected with `409 Conflict`. An employee with tasks or project memberships cannot be deleted; deactivate the employee instead. Task references use `SET NULL` on employee/project deletion at the database level, while API validation protects active associations. Project progress is computed from the associated tasks' actual `completed` statuses.

## Database notes

SQLAlchemy models are in `backend/app/db/models.py`. On startup, additive compatibility code preserves the original `company_config` table and its data. `Base.metadata.create_all` creates newly introduced tables. Department names and project names are unique; employee names are unique within a department. SQLite foreign-key enforcement is enabled for every connection. No database file is deleted or recreated by startup.

## Tests and validation

Backend tests:

```powershell
cd backend
python -m pytest -q
```

Frontend type check and production build:

```powershell
cd frontend
npm run lint
npm run build
```

## Configuration and scope

Backend settings are read from `backend/.env`; frontend only reads the public API URL from `frontend/.env.local`. Never place AI credentials in frontend configuration. `AI_PROVIDER`, `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL` remain unused placeholders until a later phase. This phase does not execute AI agents, send external messages, or connect to 9Router.
