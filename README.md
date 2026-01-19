<<<<<<< HEAD
# 3rdgenloan
=======
# Loan Management System

A Django + Supabase (PostgreSQL) web application for managing loan applications, approvals, balances, and withdrawals (request-only, no payments).

## Features
- User and admin roles
- Custom user model
- Profile and bank details onboarding
- Loan application and approval workflow
- Withdrawal request system
- Admin dashboard and audit logging
- Supabase PostgreSQL backend
- Secure, environment-based settings

## Setup

1. Clone the repository and navigate to the project root.
2. Create a Python virtual environment and activate it:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your values:
   ```sh
   cp .env.example .env
   # Edit .env with your credentials
   ```
5. Run migrations:
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Create a superuser:
   ```sh
   python manage.py createsuperuser
   ```
7. Start the development server:
   ```sh
   python manage.py runserver
   ```

## Deployment
- Use `core/settings/prod.py` for production settings.
- Set environment variables for `SECRET_KEY`, `DATABASE_URL`, and `DJANGO_ALLOWED_HOSTS` in production.
- Deploy to Fly.io or your preferred platform.

## Security
- No payments or bank APIs
- All money movement is manual and office-controlled
- Sensitive settings are loaded from environment variables
- Production settings enforce HTTPS, secure cookies, and HSTS

## License
MIT
>>>>>>> eae7749 (Initial Commit)
