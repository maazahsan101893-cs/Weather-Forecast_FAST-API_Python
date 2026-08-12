# AI FastAPI Project

A simple REST API developed using **FastAPI** for an AI/Python internship task.

The application provides:

- User signup
- User login
- Secure password hashing
- MySQL database integration
- Seven-day weather forecast
- API documentation through Swagger UI
- API testing using Python requests

---

## 1. Project Overview

The objective of this project is to develop a FastAPI-based backend application that provides user authentication and weather forecasting.

The application stores registered users in a MySQL database and retrieves seven days of weather forecast data using the Open-Meteo API.

---

## 2. Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| SQLAlchemy | Database ORM |
| MySQL | Database |
| PyMySQL | MySQL database driver |
| Passlib | Password hashing |
| Pydantic | Data validation |
| Requests | External API requests |
| Open-Meteo | Weather forecast API |
| Swagger UI | API testing and documentation |

---

## 3. Project Structure

```text
ai-python-internship/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
│
├── test_api.py
├── requirements.txt
├── config.json
├── .gitignore
└── README.md
