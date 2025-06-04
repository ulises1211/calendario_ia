from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
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

DATA_FILE = os.path.join(os.path.dirname(__file__), "appointments.json")

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
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return [Appointment(**item) for item in data]


def save_appointments(appts: List[Appointment]):
    with open(DATA_FILE, "w") as f:
        json.dump([appt.dict() for appt in appts], f, indent=2)

@app.get("/appointments", response_model=List[Appointment])
def get_appointments():
    return load_appointments()

@app.post("/appointments", response_model=Appointment)
def create_appointment(appt: Appointment):
    appts = load_appointments()
    if any(a.id == appt.id for a in appts):
        raise HTTPException(status_code=400, detail="ID already exists")
    appts.append(appt)
    save_appointments(appts)
    return appt

@app.post("/appointments/{appt_id}/validate", response_model=Appointment)
def validate_payment(appt_id: int, yape_code: str):
    appts = load_appointments()
    for appt in appts:
        if appt.id == appt_id:
            if appt.yape_code == yape_code:
                appt.confirmed = True
                save_appointments(appts)
                return appt
            else:
                raise HTTPException(status_code=400, detail="Yape code mismatch")
    raise HTTPException(status_code=404, detail="Appointment not found")


# --- User database helpers ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
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
