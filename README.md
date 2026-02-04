# Employee Management & Task Tracking System

A comprehensive full-stack application for managing employees, departments, projects, and tasks within an organization.

## Features

### Backend (FastAPI)
- **JWT Authentication** - Secure login with token-based authentication
- **Role-Based Access Control** - Admin, Manager, and Employee roles
- **CRUD Operations** - Complete management for Employees, Departments, Projects, and Tasks
- **Task Workflow** - Assigned → In Progress → Completed
- **API Validations** - Input validation, error handling, pagination, and filtering

### Database (MySQL)
- **Relational Schema Design** - Properly normalized tables with relationships
- **Soft Delete** - Data preservation with is_deleted flag
- **Audit Fields** - created_at, updated_at, created_by tracking
- **Indexed Queries** - Optimized for performance

### Frontend (HTML/CSS/JS)
- **Responsive Design** - Works on desktop and mobile
- **Role-Based Dashboards** - Different views for Admin, Manager, Employee
- **Modern UI** - Clean, professional interface with animations
- **Real-time Updates** - Dynamic content loading

### Security
- **Password Hashing** - bcrypt encryption
- **SQL Injection Prevention** - Parameterized queries via SQLAlchemy ORM
- **XSS Protection** - Input sanitization
- **CORS Configuration** - Controlled cross-origin access

##  Project Structure

```
employee_management_system/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── employee.py
│   │   ├── department.py
│   │   ├── project.py
│   │   └── task.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── employee.py
│   │   ├── department.py
│   │   ├── project.py
│   │   └── task.py
│   ├── routers/             # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── employees.py
│   │   ├── departments.py
│   │   ├── projects.py
│   │   └── tasks.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── crud.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── security.py
│       └── logger.py
├── static/                  # Frontend files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── index.html
├── migrations/              # Database migrations
├── tests/                   # Unit tests
├── requirements.txt
├── .env.example
└── README.md
```

##  Installation & Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip

### 1. Clone and Setup Virtual Environment
```bash
cd employee_management_system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Database
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE employee_management;
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Run Migrations
```bash
alembic upgrade head
```

### 5. Start the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the Application
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

##  Default Users

| Role     | Email              | Password  |
|----------|-------------------|-----------|
| Admin    | admin@company.com | admin123  |
| Manager  | manager@company.com | manager123 |
| Employee | employee@company.com | employee123 |

##  API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user

### Employees
- `GET /api/employees` - List employees (with pagination & filtering)
- `POST /api/employees` - Create employee
- `GET /api/employees/{id}` - Get employee details
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Soft delete employee

### Departments
- `GET /api/departments` - List departments
- `POST /api/departments` - Create department
- `GET /api/departments/{id}` - Get department details
- `PUT /api/departments/{id}` - Update department
- `DELETE /api/departments/{id}` - Soft delete department

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Soft delete project

### Tasks
- `GET /api/tasks` - List tasks (with filtering by status, assignee)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}/status` - Update task status (workflow)
- `DELETE /api/tasks/{id}` - Soft delete task

##  Role Permissions

| Action | Admin | Manager | Employee |
|--------|-------|---------|----------|
| View All Employees | Y | Y | N |
| Manage Employees | Y | N | N |
| Manage Departments | Y | N | N |
| Create Projects | Y | Y | N |
| Assign Tasks | Y | Y | N |
| Update Own Tasks | Y | Y | Y |
| View Dashboard Stats | Y | Y | N |

##  License

MIT License - Feel free to use for educational purposes.
