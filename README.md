# ✅ Primetrade-assignment — Backend Developer Intern Assignment

> **Tech Stack:** Python + Flask | PostgreSQL | JWT Auth | React.js Frontend

---

## 📁 Project Structure

```
Primetrade-assignment/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory
│   │   ├── models/
│   │   │   ├── user.py          # User model
│   │   │   └── task.py          # Task model
│   │   ├── routes/
│   │   │   ├── auth.py          # Register, Login, /me
│   │   │   ├── tasks.py         # CRUD APIs
│   │   │   └── admin.py         # Admin-only APIs
│   │   ├── middleware/
│   │   │   └── auth.py          # Role-based decorators
│   │   └── utils/
│   │       └── helpers.py       # Validators, response helpers
│   ├── run.py                   # Entry point
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html               # React SPA (no build needed)
├── SCALABILITY.md
└── README.md
```

---

## ⚙️ Setup & Run

### 1. PostgreSQL Setup

```sql
CREATE DATABASE Primetrade-assignment_db;
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and update DATABASE_URL with your PostgreSQL credentials

# Run DB migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
flask create-admin

# Start server
python run.py
```

Backend runs at: **http://localhost:5000**

### 3. Frontend Setup

```bash
cd frontend
# No build needed! Open directly in browser:
open index.html
# OR serve with:
python -m http.server 3000
# Visit: http://localhost:3000
```

---

## 🔑 API Reference

### Base URL: `http://localhost:5000/api/v1`

### Auth Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Register new user |
| POST | `/auth/login` | Public | Login & get JWT |
| GET | `/auth/me` | JWT | Get current user |

### Task Endpoints (JWT Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | Get all my tasks |
| GET | `/tasks?status=pending` | Filter by status |
| GET | `/tasks/:id` | Get single task |
| POST | `/tasks` | Create task |
| PUT | `/tasks/:id` | Update task |
| DELETE | `/tasks/:id` | Delete task |

### Admin Endpoints (Admin JWT Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | All users |
| PATCH | `/admin/users/:id/deactivate` | Deactivate user |
| PATCH | `/admin/users/:id/activate` | Activate user |
| GET | `/admin/stats` | Platform stats |
| GET | `/admin/tasks` | All tasks |

---

## 📖 API Documentation (Swagger)

After starting the backend, visit:
**http://localhost:5000/apidocs**

Full interactive documentation with all endpoints, request schemas, and try-it-out.

---

## 👤 Default Admin Credentials

```
Email:    admin@Primetrade-assignment.com
Password: Admin@123
```

---

## 🔒 Security Features

- **Password Hashing** — bcrypt with salt rounds
- **JWT Authentication** — stateless, expiry-based tokens
- **Role-Based Access** — user vs admin decorators
- **Input Sanitization** — all inputs stripped and length-limited
- **Input Validation** — email format, password strength, enum values
- **CORS** — configured for API routes only

---

## 🗄️ Database Schema

### `users` Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| username | VARCHAR(80) UNIQUE | Display name |
| email | VARCHAR(120) UNIQUE | Login email |
| password_hash | VARCHAR(255) | bcrypt hash |
| role | VARCHAR(20) | 'user' or 'admin' |
| is_active | BOOLEAN | Account status |
| created_at | TIMESTAMP | Registration time |

### `tasks` Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| title | VARCHAR(200) | Task name |
| description | TEXT | Optional details |
| status | VARCHAR(20) | pending / in_progress / completed |
| priority | VARCHAR(10) | low / medium / high |
| due_date | TIMESTAMP | Optional deadline |
| user_id | INTEGER FK | Owner (users.id) |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

---

## 🧪 Quick Test with curl

```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@test.com","password":"pass1234"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@test.com","password":"pass1234"}'

# Create Task (replace TOKEN)
curl -X POST http://localhost:5000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title":"Buy groceries","priority":"high","status":"pending"}'
```
