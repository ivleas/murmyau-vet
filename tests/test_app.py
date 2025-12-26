# tests/test_app.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pytest
from httpx import AsyncClient, ASGITransport
from main import app, lifespan

@pytest.mark.asyncio
async def test_home():
    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.get("/")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_add():
    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/add", data={
                "pet_name": "Мурзик",
                "owner_name": "Анна",
                "service": "Прививка",
                "appointment_date": "2025-12-30"
            })
    assert r.status_code == 303