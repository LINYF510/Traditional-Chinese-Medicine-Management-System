# TCM Management System (Django + Vue3)

Backend stack:
- Python 3.11.9+
- Django 5.2
- Django REST Framework
- JWT auth (simplejwt)
- RBAC (DRF permission class + role menu API)
- MySQL as default runtime database

Frontend stack:
- Vue 3 + Vite
- Pinia
- Vue Router
- Axios

## Features

- JWT login/refresh APIs
- Role-based menu and permission checks
- Unified API error response (`code/message/errors`)
- Dashboard, herbs, formulas, inventory modules
- Vue3 pages for dashboard/herbs/formulas/inventory

## Project structure

- Django backend: repository root
- Vue frontend: `frontend/`

## Backend setup (MySQL)

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Configure MySQL env vars (PowerShell example)

```powershell
$env:MYSQL_DATABASE="zhongyao"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="123456"
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
```

Notes:
- Runtime defaults to MySQL database `zhongyao`.
- For local fallback to SQLite, set: `$env:USE_SQLITE="1"`.
- Test runs auto-switch to SQLite.

3. Create database, migrate, seed, and run

```bash
mysql -uroot -p123456 -e "CREATE DATABASE IF NOT EXISTS zhongyao DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Or run one command in PowerShell:

```powershell
.\start_backend.ps1
```

Demo accounts:
- `admin / admin123456`
- `pharmacist / pharmacist123`
- `assistant / assistant123`

## Frontend setup (Vue3)

```bash
cd frontend
npm install
npm run dev
```

Default frontend URL: `http://127.0.0.1:5173`

Vite proxy targets Django API at `http://127.0.0.1:8000` by default.

Optional frontend env (`frontend/.env`):

```env
VITE_API_BASE_URL=
VITE_API_PROXY=http://127.0.0.1:8000
```

## API examples

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/access/`
- `GET /api/herbs/`
- `GET /api/formulas/`
- `GET /api/inventory/stocks/`
- `POST /api/inventory/inbound/`
- `POST /api/inventory/outbound/`

## Tests

```bash
python manage.py test
```
