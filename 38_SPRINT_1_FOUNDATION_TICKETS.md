# 38_SPRINT_1_FOUNDATION_TICKETS

## Purpose
Sprint 1 establishes the technical foundation for Evercrafted Studio MVP.

## Sprint Goal
Create a working app foundation with frontend, backend, database, authentication, and environment configuration.

## Ticket 1.1 — Repository Structure
Tasks:
- Create frontend app.
- Create backend app.
- Add shared types folder if needed.
- Add README with setup steps.

Acceptance:
- Frontend runs locally.
- Backend runs locally.
- README explains setup.

## Ticket 1.2 — Frontend App Shell
Tasks:
- Sidebar navigation.
- Topbar.
- Page container.
- Placeholder routes: Dashboard, Memory Weaver, Design Studio, Inventory Weaver, Design Library, Build Sheets, Render Studio, Settings.

Acceptance:
- User can navigate between placeholder pages.
- Sidebar/topbar persist.

## Ticket 1.3 — Backend API Shell
Tasks:
- Add health endpoint.
- Add API version prefix.
- Add error response format.
- Add basic logging.

Acceptance:
- `GET /api/v1/health` returns healthy status.

## Ticket 1.4 — Database Setup
Tasks:
- Configure PostgreSQL.
- Add migrations.
- Add users, blueprints, inventory tables.

Acceptance:
- Migrations run.
- Backend connects to DB.

## Ticket 1.5 — Authentication MVP
Tasks:
- Signup.
- Login.
- JWT/session handling.
- Current user endpoint.
- Protect blueprint/inventory routes.

Acceptance:
- User can sign up/log in.
- Protected endpoints require auth.
- User can only access own data.

## Ticket 1.6 — Environment Configuration
Tasks:
- Add `.env.example`.
- Document env vars.
- Keep AI API key server-side only.

Acceptance:
- No secret keys in frontend code.

## Sprint 1 Done When
Frontend shell, backend, database, auth, and protected routes work.
