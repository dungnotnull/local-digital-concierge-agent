from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from ..database.db_client import db
from ..models import Bill, ServiceProvider, MaintenanceItem, Reminder
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Local Digital Concierge API")

# Dependency to get DB
async def get_db():
    return db

# --- Bill Endpoints ---
@app.get("/bills", response_model=List[Bill])
async def get_bills():
    rows = await db.fetch_all("SELECT * FROM bills ORDER BY due_date")
    bills = []
    for row in rows:
        bills.append(Bill(
            id=row[0],
            bill_type=row[1],
            issuer=row[2],
            account_number=row[3],
            amount_due=row[4],
            due_date=row[5],
            billing_period_from=row[6],
            billing_period_to=row[7],
            status=row[8],
            paid_date=row[9],
            paid_amount=row[10],
            image_path=row[11],
            notes=row[12],
            created_at=row[13],
            updated_at=row[14]
        ))
    return bills

@app.post("/bills", response_model=Bill)
async def create_bill(bill: Bill):
    await db.execute("""
        INSERT INTO bills (bill_type, issuer, account_number, amount_due, due_date,
                           billing_period_from, billing_period_to, status, paid_date, paid_amount, image_path, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bill.bill_type,
        bill.issuer,
        bill.account_number,
        bill.amount_due,
        bill.due_date,
        bill.billing_period_from,
        bill.billing_period_to,
        bill.status,
        bill.paid_date,
        bill.paid_amount,
        bill.image_path,
        bill.notes
    ))
    row = await db.fetch_one("SELECT last_insert_rowid()")
    bill.id = row[0]
    return bill

@app.put("/bills/{bill_id}", response_model=Bill)
async def update_bill(bill_id: int, bill: Bill):
    await db.execute("""
        UPDATE bills SET
            bill_type = ?, issuer = ?, account_number = ?, amount_due = ?, due_date = ?,
            billing_period_from = ?, billing_period_to = ?, status = ?,
            paid_date = ?, paid_amount = ?, image_path = ?, notes = ?,
            updated_at = datetime('now')
        WHERE id = ?
    """, (
        bill.bill_type,
        bill.issuer,
        bill.account_number,
        bill.amount_due,
        bill.due_date,
        bill.billing_period_from,
        bill.billing_period_to,
        bill.status,
        bill.paid_date,
        bill.paid_amount,
        bill.image_path,
        bill.notes,
        bill_id
    ))
    bill.id = bill_id
    return bill

# --- Service Provider Endpoints ---
@app.get("/service-providers", response_model=List[ServiceProvider])
async def get_service_providers(category: Optional[str] = None):
    if category:
        rows = await db.fetch_all("SELECT * FROM service_providers WHERE category = ? ORDER BY trust_level DESC, rating DESC", (category,))
    else:
        rows = await db.fetch_all("SELECT * FROM service_providers ORDER BY trust_level DESC, rating DESC")
    providers = []
    for row in rows:
        providers.append(ServiceProvider(
            id=row[0],
            name=row[1],
            category=row[2],
            phone=row[3],
            address=row[4],
            latitude=row[5],
            longitude=row[6],
            distance_meters=row[7],
            trust_level=row[8],
            rating=row[9],
            notes=row[10],
            times_used=row[11],
            last_used=row[12],
            is_favorite=bool(row[13]),
            source=row[14],
            created_at=row[15],
            updated_at=row[16]
        ))
    return providers

@app.post("/service-providers", response_model=ServiceProvider)
async def create_service_provider(provider: ServiceProvider):
    await db.execute("""
        INSERT INTO service_providers (name, category, phone, address, latitude, longitude, trust_level, rating, notes, times_used, last_used, is_favorite, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        provider.name,
        provider.category,
        provider.phone,
        provider.address,
        provider.latitude,
        provider.longitude,
        provider.trust_level,
        provider.rating,
        provider.notes,
        provider.times_used,
        provider.last_used,
        provider.is_favorite,
        provider.source
    ))
    row = await db.fetch_one("SELECT last_insert_rowid()")
    provider.id = row[0]
    return provider

# --- Maintenance Item Endpoints ---
@app.get("/maintenance-items", response_model=List[MaintenanceItem])
async def get_maintenance_items():
    rows = await db.fetch_all("SELECT * FROM maintenance_items")
    items = []
    for row in rows:
        items.append(MaintenanceItem(
            id=row[0],
            item_name=row[1],
            item_type=row[2],
            interval_type=row[3],
            interval_days=row[4],
            interval_km=row[5],
            last_service_date=row[6],
            last_service_odometer=row[7],
            next_service_date=row[8],
            next_service_odometer=row[9],
            current_odometer=row[10],
            preferred_provider_id=row[11],
            notes=row[12],
            created_at=row[13]
        ))
    return items

@app.post("/maintenance-items", response_model=MaintenanceItem)
async def create_maintenance_item(item: MaintenanceItem):
    await db.execute("""
        INSERT INTO maintenance_items (item_name, item_type, interval_type, interval_days, interval_km, last_service_date, last_service_odometer, preferred_provider_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item.item_name,
        item.item_type,
        item.item_type,
        item.interval_days,
        item.interval_km,
        item.last_service_date,
        item.last_service_odometer,
        item.preferred_provider_id,
        item.notes
    ))
    row = await db.fetch_one("SELECT last_insert_rowid()")
    item.id = row[0]
    return item

# --- Household Endpoint ---
@app.get("/household")
async def get_household():
    row = await db.fetch_one("SELECT * FROM household LIMIT 1")
    if not row:
        raise HTTPException(status_code=404, detail="Household not configured")
    return {
        "id": row[0],
        "name": row[1],
        "address": row[2],
        "latitude": row[3],
        "longitude": row[4],
        "district": row[5],
        "city": row[6],
        "default_search_radius_km": row[7],
        "reminder_days_before": row[8],
        "currency": row[9],
        "timezone": row[10],
        "created_at": row[11]
    }

@app.put("/household")
async def update_household(household: dict):
    await db.execute("""
        UPDATE household SET
            name = ?, address = ?, latitude = ?, longitude = ?,
            district = ?, city = ?, default_search_radius_km = ?,
            reminder_days_before = ?, currency = ?, timezone = ?
        WHERE id = 1
    """, (
        household.get("name"),
        household.get("address"),
        household.get("latitude"),
        household.get("longitude"),
        household.get("district"),
        household.get("city"),
        household.get("default_search_radius_km", 3.0),
        household.get("reminder_days_before", 3),
        household.get("currency", "VND"),
        household.get("timezone", "Asia/Ho_Chi_Minh")
    ))
    return {"status": "updated"}

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    await db.connect()
    from ..database.migration import init_db
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await db.close()
