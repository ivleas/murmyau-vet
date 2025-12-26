# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import date
from databases import Database
from sqlalchemy import MetaData, Table, Column, Integer, String, Date

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/vetdb"
database = Database(DATABASE_URL)
metadata = MetaData()

appointments = Table(
    "appointments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("pet_name", String, nullable=False),
    Column("owner_name", String, nullable=False),
    Column("service", String, nullable=False),
    Column("appointment_date", Date, nullable=False),
    Column("notes", String, nullable=True),
)

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await database.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            pet_name VARCHAR NOT NULL,
            owner_name VARCHAR NOT NULL,
            service VARCHAR NOT NULL,
            appointment_date DATE NOT NULL,
            notes TEXT
        )
    """)
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    apps = await database.fetch_all(
        appointments.select().order_by(appointments.c.appointment_date)
    )
    today = date.today()
    today_count = sum(1 for app in apps if app["appointment_date"] == today)

    msg = request.query_params.get("msg")
    return templates.TemplateResponse(request, "index.html", {
        "appointments": apps,
        "msg": msg,
        "today_count": today_count,
        "today_str": today.isoformat(),
    })


@app.post("/add")
async def add_appointment(
    pet_name: str = Form(...),
    owner_name: str = Form(...),
    service: str = Form(...),
    appointment_date: date = Form(...),
    notes: str = Form("")
):
    if appointment_date < date.today():
        return RedirectResponse("/?msg=past_date", status_code=303)
    await database.execute(
        appointments.insert().values(
            pet_name=pet_name,
            owner_name=owner_name,
            service=service,
            appointment_date=appointment_date,
            notes=notes  # ← сохраняем
        )
    )
    return RedirectResponse("/?msg=added", status_code=303)


@app.post("/add-today")
async def add_appointment_today(
    pet_name: str = Form(...),
    owner_name: str = Form(...),
    service: str = Form(...),
    notes: str = Form("")
):
    await database.execute(
        appointments.insert().values(
            pet_name=pet_name,
            owner_name=owner_name,
            service=service,
            appointment_date=date.today(),
            notes=notes  # ← сохраняем
        )
    )
    return RedirectResponse("/?msg=added", status_code=303)


@app.post("/delete/{app_id}")
async def delete_appointment(app_id: int):
    result = await database.execute(appointments.delete().where(appointments.c.id == app_id))
    if not result:
        return RedirectResponse("/?msg=not_found", status_code=303)
    return RedirectResponse("/?msg=deleted", status_code=303)


@app.post("/reschedule/{app_id}")
async def reschedule_appointment(app_id: int, new_date: date = Form(...)):
    if new_date < date.today():
        return RedirectResponse("/?msg=past_date", status_code=303)
    result = await database.execute(
        appointments.update()
        .where(appointments.c.id == app_id)
        .values(appointment_date=new_date)
    )
    if not result:
        return RedirectResponse("/?msg=not_found", status_code=303)
    return RedirectResponse("/?msg=rescheduled", status_code=303)