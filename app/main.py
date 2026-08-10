from datetime import datetime, timedelta
import json

import requests
from fastapi import Depends, FastAPI, HTTPException
from passlib.context import CryptContext
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from pydantic import BaseModel, EmailStr
from urllib.parse import quote_plus

# -------------------- Configuration --------------------

with open("config.json", "r") as file:
    config = json.load(file)


# -------------------- Database Setup --------------------

password = quote_plus(config["db_password"])

DATABASE_URL = (
    f"mysql+pymysql://{config['db_user']}:{password}"
    f"@{config['db_host']}:{config['db_port']}/{config['db_name']}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# -------------------- Password Security --------------------

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# -------------------- Database Model --------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


# -------------------- Pydantic Models --------------------

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# -------------------- FastAPI Application --------------------

app = FastAPI(
    title="Weather Forecast API",
    version="1.0"
)


# -------------------- Database Dependency --------------------

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# -------------------- Home Route --------------------

@app.get("/")
def home():
    return {
        "message": "Weather Forecast API is running",
        "status": "Connected to MySQL",
        "endpoints": {
            "signup": "POST /signup",
            "login": "POST /login",
            "weather": "GET /weather/forecast"
        }
    }


# -------------------- Signup Route --------------------

@app.post("/signup")
def signup(
    user: SignupRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        (User.username == user.username) |
        (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    }


# -------------------- Login Route --------------------

@app.post("/login")
def login(
    user: LoginRequest,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not pwd_context.verify(
        user.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "username": db_user.username,
        "email": db_user.email
    }


# -------------------- Weather Forecast Route --------------------

@app.get("/weather/forecast")
def weather_forecast(
    start_date: str,
    latitude: float = 33.6844,
    longitude: float = 73.0479
):
    try:
        start = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        )

        end_date = start + timedelta(days=6)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "weathercode"
        ),
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date.strftime("%Y-%m-%d")
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Could not reach weather service"
        )

    data = response.json().get("daily", {})

    if not data:
        raise HTTPException(
            status_code=502,
            detail="Unexpected response from weather service"
        )

    forecast = []

    for i, day in enumerate(data["time"]):
        forecast.append({
            "date": day,
            "max_temp_c": data["temperature_2m_max"][i],
            "min_temp_c": data["temperature_2m_min"][i],
            "precipitation_mm": data["precipitation_sum"][i],
            "weather_code": data["weathercode"][i]
        })

    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "start_date": start_date,
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_days": len(forecast),
        "forecast": forecast
    }