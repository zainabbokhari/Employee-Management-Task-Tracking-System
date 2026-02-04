"""
Employee Management & Task Tracking System
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.database import Base, get_engine, get_session_local
from app.utils.logger import logger, log_request, log_error
from app.routers import auth, departments, employees, projects, tasks, users, invite

# Import models to register them with SQLAlchemy
from app.models import User, Department, Employee, Project, Task


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Employee Management System...")
    
    # Create database tables using the current engine (supports test override)
    try:
        current_engine = get_engine()
        Base.metadata.create_all(bind=current_engine)
        logger.info("Database tables created successfully")
        
    # Create default admin user if not exists (controlled by settings.CREATE_DEMO_USERS)
        from app.services.auth import AuthService
        from app.schemas.user import UserCreate
        from app.models.user import UserRole
        
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            if settings.CREATE_DEMO_USERS:
                # Check if admin exists
                existing_admin = db.query(User).filter(User.email == "admin@company.com").first()
                if not existing_admin:
                    admin_user = UserCreate(
                        email="admin@company.com",
                        password="admin123",
                        full_name="System Administrator",
                        role=UserRole.ADMIN
                    )
                    AuthService.create_user(db, admin_user)
                    logger.info("Default admin user created: admin@company.com")

                    # Create manager user
                    manager_user = UserCreate(
                        email="manager@company.com",
                        password="manager123",
                        full_name="Project Manager",
                        role=UserRole.MANAGER
                    )
                    AuthService.create_user(db, manager_user)
                    logger.info("Default manager user created: manager@company.com")

                    # Create employee user
                    employee_user = UserCreate(
                        email="employee@company.com",
                        password="employee123",
                        full_name="John Employee",
                        role=UserRole.EMPLOYEE
                    )
                    AuthService.create_user(db, employee_user)
                    logger.info("Default employee user created: employee@company.com")
            else:
                logger.info("Demo user creation disabled by settings (CREATE_DEMO_USERS=False)")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    logger.info("Application started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Employee Management System...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Employee Management & Task Tracking System
    
    A comprehensive system for managing employees, departments, projects, and tasks.
    
    ### Features:
    - 🔐 **JWT Authentication** with role-based access control
    - 👥 **Employee Management** with department assignments
    - 📁 **Project Management** with status tracking
    - ✅ **Task Workflow** (Assigned → In Progress → Completed)
    - 📊 **Dashboard Statistics** for insights
    
    ### Roles:
    - **Admin**: Full access to all features
    - **Manager**: Manage projects and tasks, view employees
    - **Employee**: View own profile, update assigned tasks
    
    ### Default Users:
    | Role | Email | Password |
    |------|-------|----------|
    | Admin | admin@company.com | admin123 |
    | Manager | manager@company.com | manager123 |
    | Employee | employee@company.com | employee123 |
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    if request.url.path.startswith("/api"):
        log_request(
            method=request.method,
            path=request.url.path,
            extra={
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s"
            }
        )
    
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    log_error(str(exc), exc_info=True, extra={"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"}
    )


# Include API routers
app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(invite.router)


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Root endpoint - serve frontend
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head>
                <title>Employee Management System</title>
                <style>
                    body { font-family: Arial; padding: 50px; text-align: center; }
                    h1 { color: #333; }
                    a { color: #007bff; }
                </style>
            </head>
            <body>
                <h1>🏢 Employee Management System</h1>
                <p>Welcome! The frontend is loading...</p>
                <p><a href="/docs">View API Documentation</a></p>
            </body>
        </html>
        """)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }


# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "departments": "/api/departments",
            "employees": "/api/employees",
            "projects": "/api/projects",
            "tasks": "/api/tasks"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
