from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Habilita CORS para cualquier origen (solo para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["http://localhost:8000"] si quieres limitarlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "users.db"

class Appointment(BaseModel):
    id: int
    name: str
    date: str
    time: str
    service: str
    yape_code: str
    confirmed: bool = False


class User(BaseModel):
    id: int
    username: str
    password: str
    name: str
    email: Optional[str] = None
    whatsapp: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    email: Optional[str] = None
    whatsapp: Optional[str] = None


class Credentials(BaseModel):
    username: str
    password: str

def load_appointments() -> List[Appointment]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, date, time, service, yape_code, confirmed FROM appointments"
    )
    rows = cur.fetchall()
    conn.close()
    return [
        Appointment(
            id=r[0],
            name=r[1],
            date=r[2],
            time=r[3],
            service=r[4],
            yape_code=r[5],
            confirmed=bool(r[6]),
        )
        for r in rows
    ]


def save_appointment(appt: Appointment):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO appointments (id, name, date, time, service, yape_code, confirmed) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                appt.id,
                appt.name,
                appt.date,
                appt.time,
                appt.service,
                appt.yape_code,
                int(appt.confirmed),
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="ID already exists")
    conn.close()

@app.get("/appointments", response_model=List[Appointment])
def get_appointments():
    return load_appointments()

@app.post("/appointments", response_model=Appointment)
def create_appointment(appt: Appointment):
    save_appointment(appt)
    return appt

@app.post("/appointments/{appt_id}/validate", response_model=Appointment)
def validate_payment(appt_id: int, yape_code: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT yape_code, confirmed FROM appointments WHERE id = ?",
        (appt_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Appointment not found")
    if row[0] != yape_code:
        conn.close()
        raise HTTPException(status_code=400, detail="Yape code mismatch")
    cur.execute(
        "UPDATE appointments SET confirmed = 1 WHERE id = ?",
        (appt_id,),
    )
    conn.commit()
    cur.execute(
        "SELECT id, name, date, time, service, yape_code, confirmed FROM appointments WHERE id = ?",
        (appt_id,),
    )
    row = cur.fetchone()
    conn.close()
    return Appointment(
        id=row[0],
        name=row[1],
        date=row[2],
        time=row[3],
        service=row[4],
        yape_code=row[5],
        confirmed=bool(row[6]),
    )


# --- User database helpers ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Table for users
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            whatsapp TEXT UNIQUE
        )"""
    )
    # Table for appointments
    cur.execute(
        """CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            service TEXT NOT NULL,
            yape_code TEXT NOT NULL,
            confirmed INTEGER NOT NULL DEFAULT 0
        )"""
    )
    conn.commit()
    conn.close()


def create_user(username: str, password: str, name: str, email: Optional[str] = None, whatsapp: Optional[str] = None) -> User:
    if not email and not whatsapp:
        raise HTTPException(status_code=400, detail="email or whatsapp required")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password, name, email, whatsapp) VALUES (?, ?, ?, ?, ?)",
            (username, password, name, email, whatsapp),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="user already exists")
    cur.execute(
        "SELECT id, username, password, name, email, whatsapp FROM users WHERE id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    return User(id=row[0], username=row[1], password=row[2], name=row[3], email=row[4], whatsapp=row[5])


def get_users() -> List[User]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, name, email, whatsapp FROM users")
    rows = cur.fetchall()
    conn.close()
    return [User(id=r[0], username=r[1], password=r[2], name=r[3], email=r[4], whatsapp=r[5]) for r in rows]


def authenticate_user(username: str, password: str) -> User:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password, name, email, whatsapp FROM users WHERE username = ? AND password = ?",
        (username, password),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="invalid credentials")
    return User(id=row[0], username=row[1], password=row[2], name=row[3], email=row[4], whatsapp=row[5])


@app.on_event("startup")
def startup_event():
    init_db()


@app.post("/users", response_model=User)
def register_user(user: UserCreate):
    return create_user(user.username, user.password, user.name, user.email, user.whatsapp)


@app.post("/login", response_model=User)
def login(creds: Credentials):
    return authenticate_user(creds.username, creds.password)


@app.get("/users", response_model=List[User])
def list_users():
    return get_users()

@app.get("/")
def root():
    return {"message": "Bienvenido al backend de Salón Booking con Yape"}
