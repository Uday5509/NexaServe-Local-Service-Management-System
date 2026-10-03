# Local Service Management System

A responsive local services booking website built with HTML, CSS, JavaScript, Bootstrap 5, Flask, and PostgreSQL.

## Features
- Responsive landing page and service catalog with search
- Customer registration and login (passwords are hashed)
- Book a service with date, address, and notes
- Customer dashboard to view booking status
- Admin dashboard to review bookings and update status
- Starter service listings seeded automatically

## Requirements
- Python 3.10+
- PostgreSQL installed and running

## Setup (Windows / VS Code)
1. Create a PostgreSQL database:
   ```sql
   CREATE DATABASE local_services;
   ```
2. Open this folder in VS Code and open the terminal:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update your PostgreSQL password and connection details.
4. Start the app:
   ```powershell
   python app.py
   ```
5. Visit http://127.0.0.1:5000

The app creates its tables and sample services on startup.

## Admin account
Register normally first. To grant admin access, run this SQL in your PostgreSQL database:
```sql
UPDATE "user" SET role = 'admin' WHERE email = 'your-email@example.com';
```
Log out and back in, then open `/admin`.

## Notes
- This is a learning/college project starter. Configure a strong `SECRET_KEY`, add CSRF protection, validation, and production deployment settings before public use.
- Booking payments are not integrated; the payments table is intentionally not included until a payment provider is selected.
