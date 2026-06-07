from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class Bill(BaseModel):
    id: Optional[int] = None
    bill_type: str
    issuer: Optional[str] = None
    account_number: Optional[str] = None
    amount_due: int
    due_date: str  # ISO format string
    billing_period_from: Optional[str] = None
    billing_period_to: Optional[str] = None
    status: str = "pending"
    paid_date: Optional[str] = None
    paid_amount: Optional[int] = None
    image_path: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @validator('bill_type')
    def validate_bill_type(cls, v):
        allowed = ['electricity', 'water', 'internet', 'phone', 'rent', 'loan', 'gas', 'other']
        if v not in allowed:
            raise ValueError(f'bill_type must be one of {allowed}')
        return v

    @validator('status')
    def validate_status(cls, v):
        allowed = ['pending', 'reminded', 'paid', 'overdue', 'cancelled']
        if v not in allowed:
            raise ValueError(f'status must be one of {allowed}')
        return v

class ServiceProvider(BaseModel):
    id: Optional[int] = None
    name: str
    category: str
    phone: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_meters: Optional[float] = None
    trust_level: int = 0
    rating: Optional[float] = None
    notes: Optional[str] = None
    times_used: int = 0
    last_used: Optional[str] = None
    is_favorite: bool = False
    source: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @validator('category')
    def validate_category(cls, v):
        allowed = ['plumbing', 'electrical', 'hvac', 'appliance', 'structural', 'pest', 'cleaning', 'other']
        if v not in allowed:
            raise ValueError(f'category must be one of {allowed}')
        return v

    @validator('trust_level')
    def validate_trust_level(cls, v):
        if v not in [0, 1, 2, 3]:
            raise ValueError('trust_level must be 0, 1, 2, or 3')
        return v

class MaintenanceItem(BaseModel):
    id: Optional[int] = None
    item_name: str
    item_type: str
    interval_type: str
    interval_days: Optional[int] = None
    interval_km: Optional[int] = None
    last_service_date: Optional[str] = None
    last_service_odometer: Optional[int] = None
    next_service_date: Optional[str] = None
    next_service_odometer: Optional[int] = None
    current_odometer: Optional[int] = None
    preferred_provider_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None

    @validator('item_type')
    def validate_item_type(cls, v):
        allowed = ['vehicle', 'appliance', 'home_system', 'other']
        if v not in allowed:
            raise ValueError(f'item_type must be one of {allowed}')
        return v

    @validator('interval_type')
    def validate_interval_type(cls, v):
        allowed = ['date_interval', 'odometer_interval', 'both']
        if v not in allowed:
            raise ValueError(f'interval_type must be one of {allowed}')
        return v

class Reminder(BaseModel):
    id: Optional[int] = None
    bill_id: Optional[int] = None
    maintenance_id: Optional[int] = None
    reminder_type: str
    scheduled_at: str  # ISO format
    fired_at: Optional[str] = None
    acknowledged_at: Optional[str] = None
    channel: str = "push"
    message: str
    snooze_count: int = 0

    @validator('reminder_type')
    def validate_reminder_type(cls, v):
        allowed = ['payment_due', 'maintenance_due', 'custom']
        if v not in allowed:
            raise ValueError(f'reminder_type must be one of {allowed}')
        return v

    @validator('channel')
    def validate_channel(cls, v):
        allowed = ['push', 'sms', 'audio', 'email']
        if v not in allowed:
            raise ValueError(f'channel must be one of {allowed}')
        return v
