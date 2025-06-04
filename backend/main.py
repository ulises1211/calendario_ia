from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

DATA_FILE = os.path.join(os.path.dirname(__file__), "appointments.json")

class Appointment(BaseModel):
    id: int
    name: str
    date: str
    time: str
    yape_code: str
    confirmed: bool = False

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
