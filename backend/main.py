from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import sqlite3

app = FastAPI()

DATA_FILE = os.path.join(os.path.dirname(__file__), "appointments.json")

DB_FILE = "users.db"

class Appointment(BaseModel):
    id: int
    name: str
    date: str
    time: str
    yape_code: str
    confirmed: bool = False


class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    whatsapp: Optional[str] = None

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
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            whatsapp TEXT UNIQUE
        )"""
    )
    conn.commit()
    conn.close()


def create_user(name: str, email: Optional[str] = None, whatsapp: Optional[str] = None) -> User:
    if not email and not whatsapp:
        raise HTTPException(status_code=400, detail="email or whatsapp required")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, whatsapp) VALUES (?, ?, ?)",
            (name, email, whatsapp),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="user already exists")
    cur.execute(
        "SELECT id, name, email, whatsapp FROM users WHERE id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    return User(id=row[0], name=row[1], email=row[2], whatsapp=row[3])


def get_users() -> List[User]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, whatsapp FROM users")
    rows = cur.fetchall()
    conn.close()
    return [User(id=r[0], name=r[1], email=r[2], whatsapp=r[3]) for r in rows]


@app.on_event("startup")
def startup_event():
    init_db()


@app.post("/users", response_model=User)
def register_user(user: User):
    return create_user(user.name, user.email, user.whatsapp)


@app.get("/users", response_model=List[User])
def list_users():
    return get_users()
