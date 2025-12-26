from pydantic import BaseModel
from datetime import date

class AppointmentBase(BaseModel):
    pet_name: str
    owner_name: str
    service: str
    appointment_date: date

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int

    class Config:
        from_attributes = True