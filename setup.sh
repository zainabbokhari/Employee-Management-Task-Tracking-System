#!/bin/bash
# Employee Management System - Setup Script for Mac/Linux

echo "=========================================="
echo "  Employee Management System Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if not exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
fi

# Initialize database
echo ""
echo "Initializing database..."
$PYTHON_CMD -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the server:"
echo "     python -m uvicorn app.main:app --reload"
echo ""
echo "  3. Open in browser:"
echo "     http://localhost:8000"
echo ""
echo "Default Login Credentials:"
echo "  Admin:    admin@company.com / admin123"
echo "  Manager:  manager@company.com / manager123"
echo "  Employee: employee@company.com / employee123"
echo ""
echo "=========================================="

# Ask if user wants to start now
read -p "Start the application now? (y/n): " START_NOW
if [ "$START_NOW" = "y" ] || [ "$START_NOW" = "Y" ]; then
    echo ""
    echo "Starting server..."
    $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
