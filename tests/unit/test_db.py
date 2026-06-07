import pytest
import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.db_client import db
from src.database.migration import init_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    # Use a test database
    db.db_path = "data/test.db"
    await db.connect()
    await init_db()
    yield
    await db.close()
    # Clean up test database
    if os.path.exists("data/test.db"):
        os.remove("data/test.db")

@pytest.mark.asyncio
async def test_db_connection():
    assert db._connection is not None

@pytest.mark.asyncio
async def test_insert_and_fetch_bill():
    # Insert a bill
    await db.execute("""
        INSERT INTO bills (bill_type, issuer, account_number, amount_due, due_date,
                           billing_period_from, billing_period_to, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ("electricity", "EVN TP.HCM", "12345678", 100000, "2025-06-30", "2025-06-01", "2025-06-30", "pending"))
    # Fetch it
    row = await db.fetch_one("SELECT * FROM bills WHERE account_number = ?", ("12345678",))
    assert row is not None
    assert row[1] == "electricity"
    assert row[2] == "EVN TP.HCM"
    assert row[3] == "12345678"
    assert row[4] == 100000
    assert row[5] == "2025-06-30"
    assert row[6] == "2025-06-01"
    assert row[7] == "2025-06-30"
    assert row[8] == "pending"

@pytest.mark.asyncio
async def test_update_bill():
    # Update the bill
    await db.execute("UPDATE bills SET amount_due = ? WHERE account_number = ?", (150000, "12345678"))
    row = await db.fetch_one("SELECT amount_due FROM bills WHERE account_number = ?", ("12345678",))
    assert row[0] == 150000

@pytest.mark.asyncio
async def test_delete_bill():
    await db.execute("DELETE FROM bills WHERE account_number = ?", ("12345678",))
    row = await db.fetch_one("SELECT * FROM bills WHERE account_number = ?", ("12345678",))
    assert row is None
