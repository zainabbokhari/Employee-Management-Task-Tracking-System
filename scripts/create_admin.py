#!/usr/bin/env python3
"""Create a user (ADMIN, MANAGER, EMPLOYEE) from the command line using AuthService.

Usage (interactive):
  python scripts/create_admin.py

Usage (non-interactive example):
  python scripts/create_admin.py --email admin@company.com --full-name "Admin Name" --role ADMIN
  (you will be prompted for password unless --password is provided)
"""
import argparse
import getpass
from app.database import get_session_local
from app.schemas.user import UserCreate
from app.services.auth import AuthService
from app.models.user import UserRole


def parse_args():
    p = argparse.ArgumentParser(description="Create a user (ADMIN/MANAGER/EMPLOYEE)")
    p.add_argument("--email", help="User email")
    p.add_argument("--full-name", dest="full_name", help="Full name")
    p.add_argument("--role", choices=[r.name for r in UserRole], default="EMPLOYEE", help="Role")
    p.add_argument("--password", help="Password (if omitted, will prompt)")
    return p.parse_args()


def main():
    args = parse_args()

    email = args.email or input("Email: ").strip()
    full_name = args.full_name or input("Full name: ").strip()
    role = args.role

    if args.password:
        pw = args.password
    else:
        pw = getpass.getpass("Password (will not echo): ")
        pw2 = getpass.getpass("Confirm password: ")
        if pw != pw2:
            print("Passwords do not match")
            return

    db = get_session_local()()
    try:
        user = UserCreate(email=email, password=pw, full_name=full_name, role=UserRole[role])
        created = AuthService.create_user(db, user)
        print(f"Created user: {created.email} (id={created.id}, role={created.role})")
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
