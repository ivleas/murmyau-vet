from databases import Database
from sqlalchemy import MetaData, Table, Column, Integer, String, Date, create_engine

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/vetdb"
database = Database(DATABASE_URL)
metadata = MetaData()

appointments = Table(
    "appointments",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("pet_name", String, nullable=False),
    Column("owner_name", String, nullable=False),
    Column("service", String, nullable=False),
    Column("appointment_date", Date, nullable=False),
)