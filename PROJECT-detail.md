# PROJECT-detail.md — local-digital-concierge-agent

**Full Technical Specification**
Version: 1.0.0 | Last Updated: 2025-06
Status: Pre-Development → Design Finalized

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [System Architecture — Local-First Design](#3-system-architecture--local-first-design)
4. [Database Schema](#4-database-schema)
5. [Component Specifications](#5-component-specifications)
6. [Bill Processing Pipeline](#6-bill-processing-pipeline)
7. [Service Finder — OSM + Places Integration](#7-service-finder--osm--places-integration)
8. [Reminder & Scheduling Engine](#8-reminder--scheduling-engine)
9. [Message Drafting Pipeline](#9-message-drafting-pipeline)
10. [Expense Tracking & Reporting](#10-expense-tracking--reporting)
11. [Maintenance Tracker](#11-maintenance-tracker)
12. [Self-Learning Knowledge System](#12-self-learning-knowledge-system)
13. [Privacy Architecture](#13-privacy-architecture)
14. [Performance Targets](#14-performance-targets)
15. [Risks & Mitigations](#15-risks--mitigations)
16. [Success Metrics](#16-success-metrics)

---

## 1. Project Overview

### 1.1 Name & Tagline
**local-digital-concierge-agent** — *"Quản gia số kết nối dịch vụ đời sống cho hộ gia đình"*
Your family's quiet digital manager — bills tracked, maintenance scheduled, repairmen found. All running on your own device.

### 1.2 The Differentiating Promise: Local-First, AI-Light

Most smart home/household management apps are cloud-based SaaS. This agent is:
- **Local-first**: Runs on a home device (Raspberry Pi, old laptop, Android phone)
- **SQLite-backed**: All data in one portable file on YOUR device
- **AI-minimal**: LLM called only for image parsing and message drafting; scheduling and search use traditional algorithms
- **Privacy by design**: Family data never goes to a cloud database

### 1.3 Target Deployment Hardware

| Option | Device | Cost | Suitability |
|--------|--------|------|-------------|
| Primary | Android phone (family spare) | 0 (reuse) | Best for non-technical families |
| Secondary | Raspberry Pi 4 (2GB) | ~600k VND | Always-on home server |
| Tertiary | Old Windows/Mac laptop | 0 (reuse) | Full web dashboard |
| Cloud (privacy-relaxed option) | VPS (Linode/DigitalOcean) | ~100k/month | Remote access needed |

---

## 2. Problem Statement

### 2.1 The Household Admin Burden

Vietnamese households manage a growing pile of recurring obligations:
- 3-5 utility bills monthly (điện, nước, internet, truyền hình cáp, gas)
- Vehicle maintenance schedules (xe máy mỗi 3,000km, oto mỗi 5,000km)
- Air conditioner cleaning every 6 months
- Water purifier filter changes every 3-6 months
- Rental payments to track and document
- Loan installments (mua xe, mua điện thoại trả góp)

The coordination cost of managing all this falls disproportionately on one family member. A missed bill payment incurs late fees. A missed oil change risks engine damage. Finding a trustworthy repairman when the water pipe bursts at 10pm is stressful and unreliable.

### 2.2 Why Existing Tools Fail for Vietnamese Households

| Tool | Gap |
|------|-----|
| Banking apps | Only handles payments, not bill tracking or service finding |
| Google Calendar | No OCR, no service finder, no bill-specific logic |
| Home maintenance apps | Not localized for VN, no Vietnamese utility integrations |
| Generic task managers | No intelligence about what "Ổn áp cần kiểm tra" actually means |
| Zalo reminder bots | No OCR, no local service search, no data persistence |

### 2.3 The "Digitally Non-Native Household" Problem

Many Vietnamese households have parents and grandparents who are the primary household managers but are not tech-savvy. They:
- Pay bills in cash at post offices (can forget due dates)
- Find repairmen through word-of-mouth (unreliable quality)
- Don't use apps for household management
- Trust their children to handle "digital stuff" but children live separately

This agent serves as that trusted digital intermediary — without requiring the elderly family member to be tech-savvy themselves.

---

## 3. System Architecture — Local-First Design

### 3.1 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION LAYER                             │
│                                                                        │
│   Mobile App (React Native)    Web Dashboard (local network only)     │
│   • Photo capture              • Full management interface            │
│   • Voice input                • Charts, history, settings           │
│   • Push notifications         • Multi-device household access       │
└──────────────────────────────────────┬───────────────────────────────┘
                                       │ HTTP to local FastAPI
┌──────────────────────────────────────▼───────────────────────────────┐
│                   LOCAL AGENT CORE (Python)                           │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │
│  │ Bill         │  │ Scheduler    │  │ Service Finder               │ │
│  │ Processor    │  │ (APScheduler)│  │ (OSM + Places API)           │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────────────┘ │
│         │                  │                                            │
│  ┌──────▼─────────────────▼──────────────────────────────────────────┐ │
│  │                    SQLITE DATABASE                                  │ │
│  │            concierge.db — ALL family data lives here               │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │
│  │ Maintenance  │  │ Expense      │  │ Message Drafter              │ │
│  │ Tracker      │  │ Tracker      │  │ (with user confirmation)     │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────────┘ │
└──────────────────────────────────────┬───────────────────────────────┘
                                       │ Minimal, privacy-safe calls
┌──────────────────────────────────────▼───────────────────────────────┐
│                 EXTERNAL SERVICES (ALL OPTIONAL)                       │
│                                                                        │
│  Claude API        OpenStreetMap    Google Places    Twilio/Zalo      │
│  (Vision + Text)   (Free, no key)   (Optional key)   (SMS, optional) │
│  Bill extraction   Nearby search    Enhanced data    Message sending  │
│  Message drafting                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 The Local-First Principle in Practice

```
CLOUD-FIRST (what we're NOT doing):
User data → Cloud DB → Processing → Response → User
                ↑
        Family bills, amounts, addresses stored on vendor servers

LOCAL-FIRST (what we ARE doing):
User data → Local SQLite → Local Processing → Response → User
                                    ↓
                    External API called with MINIMUM data
                    (only image or brief text description)
```

### 3.3 Offline Capability Matrix

| Feature | Online | Offline |
|---------|--------|---------|
| View existing bills/reminders | ✅ | ✅ |
| Receive notifications | ✅ | ✅ (local) |
| Add bill manually | ✅ | ✅ |
| Bill photo OCR | ✅ (Claude Vision) | ⚠️ (EasyOCR fallback) |
| Find service providers | ✅ | ⚠️ (cached results only) |
| Draft messages | ✅ (Claude) | ⚠️ (template fallback) |
| Expense reports | ✅ | ✅ |

---

## 4. Database Schema

```sql
-- src/database/schema.sql

-- Core bills table
CREATE TABLE bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_type TEXT NOT NULL,           -- 'electricity','water','internet','phone','rent','loan','gas','other'
    issuer TEXT,                       -- "EVN TP.HCM", "SAWACO", "VNPT"
    account_number TEXT,               -- Customer/meter number
    amount_due INTEGER NOT NULL,       -- VND (whole number)
    due_date TEXT NOT NULL,            -- ISO 8601: "2025-06-15"
    billing_period_from TEXT,          -- "2025-05-01"
    billing_period_to TEXT,            -- "2025-05-31"
    status TEXT DEFAULT 'pending',     -- 'pending','reminded','paid','overdue','cancelled'
    paid_date TEXT,                    -- When user marks as paid
    paid_amount INTEGER,               -- Actual amount paid (may differ from due)
    image_path TEXT,                   -- Local path to bill photo (optional)
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(issuer, account_number, billing_period_to) -- Prevent duplicates
);

-- Reminder schedules
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER REFERENCES bills(id) ON DELETE CASCADE,
    maintenance_id INTEGER REFERENCES maintenance_items(id) ON DELETE CASCADE,
    reminder_type TEXT NOT NULL,       -- 'payment_due','maintenance_due','custom'
    scheduled_at TEXT NOT NULL,        -- When to fire: ISO 8601
    fired_at TEXT,                     -- When actually fired
    acknowledged_at TEXT,              -- When user acknowledged
    channel TEXT DEFAULT 'push',       -- 'push','sms','audio','email'
    message TEXT NOT NULL,
    snooze_count INTEGER DEFAULT 0
);

-- Service providers (local trusted list + OSM cache)
CREATE TABLE service_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,            -- 'plumbing','electrical','hvac','appliance','structural','pest','cleaning','other'
    phone TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    distance_meters REAL,              -- Distance from home (cached)
    trust_level INTEGER DEFAULT 0,     -- 0=unknown, 1=good_rating, 2=user_trusted, 3=family_recommended
    rating REAL,                       -- From OSM/Google (0-5)
    notes TEXT,                        -- User notes: "Sạch sẽ, đúng giờ, giá hợp lý"
    times_used INTEGER DEFAULT 0,
    last_used TEXT,
    is_favorite BOOLEAN DEFAULT FALSE,
    source TEXT,                       -- 'user_added','osm','google_places','knowledge_base'
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Maintenance tracking
CREATE TABLE maintenance_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,           -- "Xe máy Honda Wave - Thay nhớt", "Điều hòa - Vệ sinh lọc"
    item_type TEXT NOT NULL,           -- 'vehicle','appliance','home_system','other'
    interval_type TEXT NOT NULL,       -- 'date_interval','odometer_interval','both'
    interval_days INTEGER,             -- e.g., 90 days between service
    interval_km INTEGER,               -- e.g., 3000 km between oil changes
    last_service_date TEXT,
    last_service_odometer INTEGER,
    next_service_date TEXT,            -- Calculated
    next_service_odometer INTEGER,     -- Calculated
    current_odometer INTEGER,          -- Updated by user
    preferred_provider_id INTEGER REFERENCES service_providers(id),
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Message drafts and send log
CREATE TABLE message_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id INTEGER REFERENCES service_providers(id),
    issue_description TEXT NOT NULL,
    draft_text TEXT NOT NULL,          -- The drafted message
    final_text TEXT,                   -- Edited version (if user modified)
    channel TEXT,                      -- 'sms','zalo','clipboard','manual'
    status TEXT DEFAULT 'draft',       -- 'draft','confirmed','sent','failed'
    sent_at TEXT,
    user_confirmed_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Home/household profile
CREATE TABLE household (
    id INTEGER PRIMARY KEY DEFAULT 1,  -- Single row
    name TEXT,                         -- "Nhà Nguyễn Văn Tám"
    address TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    district TEXT,
    city TEXT,
    default_search_radius_km REAL DEFAULT 3.0,
    reminder_days_before INTEGER DEFAULT 3,
    currency TEXT DEFAULT 'VND',
    timezone TEXT DEFAULT 'Asia/Ho_Chi_Minh',
    created_at TEXT DEFAULT (datetime('now'))
);

-- Knowledge base entries (for bill format recognition)
CREATE TABLE bill_formats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issuer TEXT NOT NULL,              -- "EVN TP.HCM"
    bill_type TEXT NOT NULL,
    format_version TEXT,               -- "2024_q1"
    keywords TEXT,                     -- JSON array of keywords to identify this bill type
    extraction_hints TEXT,             -- JSON: hints for Vision API
    sample_image_path TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for performance
CREATE INDEX idx_bills_due_date ON bills(due_date);
CREATE INDEX idx_bills_status ON bills(status);
CREATE INDEX idx_reminders_scheduled ON reminders(scheduled_at, fired_at);
CREATE INDEX idx_providers_category ON service_providers(category, trust_level);
CREATE INDEX idx_maintenance_next_service ON maintenance_items(next_service_date);
```

---

## 5. Component Specifications

### 5.1 Bill Processor (`src/agents/bill-processor/`)

```python
# src/agents/bill-processor/processor.py

from dataclasses import dataclass
from typing import Optional
import anthropic
import aiosqlite
from datetime import datetime, timedelta

@dataclass
class BillData:
    bill_type: str
    issuer: Optional[str]
    account_number: Optional[str]
    amount_due: int         # VND
    due_date: str           # ISO 8601
    billing_period_from: Optional[str]
    billing_period_to: Optional[str]
    payment_methods: list[str]
    confidence: float       # 0-1, how confident the extraction is

class BillProcessor:
    def __init__(self, db: aiosqlite.Connection, claude_client: anthropic.Anthropic):
        self.db = db
        self.claude = claude_client
    
    async def process_bill_image(self, image_bytes: bytes) -> BillData:
        """Extract structured data from a bill photo."""
        
        # Step 1: Load known bill formats from KB (helps Vision API)
        known_formats = await self.load_known_formats()
        
        # Step 2: Call Vision API
        raw_data = await self._call_vision_api(image_bytes, known_formats)
        
        # Step 3: Validate and normalize
        validated = self._validate_extraction(raw_data)
        
        # Step 4: Check for duplicates
        is_duplicate = await self._check_duplicate(validated)
        
        if not is_duplicate:
            # Step 5: Save to database
            bill_id = await self._save_bill(validated, image_bytes)
            
            # Step 6: Create reminders
            await self._create_reminders(bill_id, validated.due_date)
        
        return validated
    
    async def _call_vision_api(
        self, image_bytes: bytes, known_formats: list
    ) -> dict:
        """Call Claude Vision with privacy-safe context."""
        
        # Load format hints for common Vietnamese issuers
        format_hints = "\n".join([
            f"- {f['issuer']}: look for '{f['keywords']}'"
            for f in known_formats[:10]  # Top 10 most common
        ])
        
        prompt = BILL_EXTRACTION_PROMPT.format(format_hints=format_hints)
        
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64.b64encode(image_bytes).decode()
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }]
        )
        
        return json.loads(response.content[0].text)
    
    async def _check_duplicate(self, bill: BillData) -> bool:
        """Check if this bill was already recorded."""
        async with self.db.execute(
            """SELECT id FROM bills 
               WHERE issuer = ? AND account_number = ? 
               AND billing_period_to = ? AND ABS(amount_due - ?) < 1000""",
            (bill.issuer, bill.account_number, bill.billing_period_to, bill.amount_due)
        ) as cursor:
            return await cursor.fetchone() is not None
    
    def _validate_extraction(self, raw: dict) -> BillData:
        """Validate extracted data against business rules."""
        
        if raw.get("error"):
            raise ValueError(f"Not a bill: {raw['error']}")
        
        # Due date must be in the future (or recent past — late bill)
        due_date = datetime.fromisoformat(raw["due_date"])
        if due_date < datetime.now() - timedelta(days=90):
            raise ValueError("Bill due date is more than 90 days ago — possibly wrong extraction")
        
        # Amount must be positive and reasonable (< 100 million VND for household)
        if not (0 < raw["amount_due"] < 100_000_000):
            raise ValueError(f"Unusual amount: {raw['amount_due']}")
        
        return BillData(**raw, confidence=self._calculate_confidence(raw))
    
    def _calculate_confidence(self, raw: dict) -> float:
        """How confident are we in this extraction? (0-1)"""
        score = 0.0
        if raw.get("amount_due"): score += 0.3
        if raw.get("due_date"): score += 0.3
        if raw.get("issuer"): score += 0.2
        if raw.get("billing_period_to"): score += 0.2
        return score
```

**Fallback OCR (when Vision API unavailable):**
```python
import easyocr

class FallbackOCR:
    def __init__(self):
        self.reader = easyocr.Reader(['vi', 'en'], gpu=False)
        self.bill_patterns = load_bill_regex_patterns()
    
    def extract_bill_text(self, image_bytes: bytes) -> dict:
        """Extract text using EasyOCR, parse with regex patterns."""
        results = self.reader.readtext(image_bytes)
        full_text = " ".join([text for _, text, _ in results if conf > 0.5])
        
        # Apply regex patterns for known Vietnamese bill formats
        extracted = {}
        for field, pattern in self.bill_patterns.items():
            match = re.search(pattern, full_text)
            if match:
                extracted[field] = match.group(1)
        
        return extracted
```

### 5.2 Reminder & Scheduling Engine (`src/agents/scheduler/`)

```python
# src/agents/scheduler/reminder_engine.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
import aiosqlite

class ReminderEngine:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.notifier = NotificationManager()
    
    async def initialize(self):
        """Load all pending reminders from DB and schedule them."""
        self.scheduler.start()
        
        # Load pending reminders
        async with self.db.execute(
            "SELECT * FROM reminders WHERE fired_at IS NULL AND scheduled_at > datetime('now')"
        ) as cursor:
            pending = await cursor.fetchall()
        
        for reminder in pending:
            self._schedule_reminder(reminder)
        
        # Schedule recurring jobs
        self.scheduler.add_job(
            self._check_overdue_bills,
            CronTrigger(hour=9, minute=0),  # 9 AM daily
            id="overdue_check"
        )
        
        self.scheduler.add_job(
            self._generate_monthly_summary,
            CronTrigger(day=1, hour=8, minute=0),  # 1st of each month
            id="monthly_summary"
        )
    
    def _schedule_reminder(self, reminder: dict):
        """Add a single reminder to APScheduler."""
        self.scheduler.add_job(
            self._fire_reminder,
            DateTrigger(run_date=reminder["scheduled_at"]),
            args=[reminder["id"]],
            id=f"reminder_{reminder['id']}",
            replace_existing=True
        )
    
    async def _fire_reminder(self, reminder_id: int):
        """Fire a reminder notification."""
        reminder = await self.db.execute_one(
            "SELECT r.*, b.amount_due, b.issuer, b.due_date FROM reminders r "
            "LEFT JOIN bills b ON r.bill_id = b.id WHERE r.id = ?",
            (reminder_id,)
        )
        
        # Format message
        message = self._format_reminder_message(reminder)
        
        # Send via configured channel
        await self.notifier.send(
            channel=reminder["channel"],
            title="💳 Nhắc nhở thanh toán",
            message=message,
            data={"reminder_id": reminder_id, "bill_id": reminder.get("bill_id")}
        )
        
        # Mark as fired
        await self.db.execute(
            "UPDATE reminders SET fired_at = datetime('now') WHERE id = ?",
            (reminder_id,)
        )
        
        # Schedule escalation if not acknowledged within 24 hours
        escalation_time = datetime.now() + timedelta(hours=24)
        if reminder["snooze_count"] < 2:
            self.scheduler.add_job(
                self._escalate_reminder,
                DateTrigger(run_date=escalation_time),
                args=[reminder_id]
            )
    
    def _format_reminder_message(self, reminder: dict) -> str:
        """Format user-friendly Vietnamese reminder message."""
        if reminder["reminder_type"] == "payment_due":
            days_until = (
                datetime.fromisoformat(reminder["due_date"]) - datetime.now()
            ).days
            
            amount = f"{reminder['amount_due']:,}".replace(",", ".")
            
            if days_until == 0:
                return f"⚠️ {reminder['issuer']}: {amount} đ phải thanh toán HÔM NAY!"
            elif days_until == 1:
                return f"⚠️ {reminder['issuer']}: {amount} đ đến hạn ngày mai!"
            else:
                return f"📅 {reminder['issuer']}: {amount} đ đến hạn sau {days_until} ngày"
        
        elif reminder["reminder_type"] == "maintenance_due":
            return f"🔧 {reminder['message']}"
        
        return reminder["message"]
    
    async def create_bill_reminders(self, bill_id: int, due_date: str, days_before: int = 3):
        """Create standard reminder sequence for a new bill."""
        due = datetime.fromisoformat(due_date)
        
        reminders = [
            (due - timedelta(days=days_before), "payment_due", "push"),
            (due - timedelta(days=1), "payment_due", "push"),
            (due, "payment_due", "push"),  # Day-of reminder
        ]
        
        for scheduled_at, reminder_type, channel in reminders:
            if scheduled_at > datetime.now():
                await self.db.execute(
                    """INSERT INTO reminders (bill_id, reminder_type, scheduled_at, channel, message)
                       VALUES (?, ?, ?, ?, ?)""",
                    (bill_id, reminder_type, scheduled_at.isoformat(), channel, "")
                )
```

### 5.3 Service Finder (`src/agents/service-finder/`)

```python
# src/agents/service-finder/finder.py

import httpx
import math
from dataclasses import dataclass

@dataclass
class ServiceProvider:
    name: str
    category: str
    phone: Optional[str]
    address: str
    latitude: float
    longitude: float
    distance_meters: float
    trust_level: int    # 0-3
    rating: Optional[float]
    source: str

class ServiceFinder:
    OSM_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    def __init__(self, db: aiosqlite.Connection, home_lat: float, home_lng: float):
        self.db = db
        self.home_lat = home_lat
        self.home_lng = home_lng
    
    async def find_providers(
        self, 
        category: str,
        radius_km: float = 3.0,
        max_results: int = 5
    ) -> list[ServiceProvider]:
        """Find service providers, prioritizing user's trusted list."""
        
        results = []
        
        # Step 1: Check user's trusted list first
        trusted = await self._get_trusted_providers(category, radius_km)
        results.extend(trusted)
        
        # Step 2: Search OpenStreetMap (free, no key, privacy-safe)
        osm_results = await self._search_osm(category, radius_km)
        
        # Step 3: Merge and deduplicate
        merged = self._merge_results(results, osm_results, max_results)
        
        # Step 4: Optionally enrich with Google Places (if key available)
        if self.google_places_key:
            merged = await self._enrich_with_google_places(merged)
        
        # Step 5: Cache results in DB for offline use
        await self._cache_results(merged, category)
        
        return merged
    
    async def _search_osm(self, category: str, radius_km: float) -> list[dict]:
        """Search OpenStreetMap for service providers."""
        
        # Map our categories to OSM tags
        osm_tags = OSM_CATEGORY_TAGS.get(category, [])
        if not osm_tags:
            return []
        
        # Build Overpass query
        radius_m = radius_km * 1000
        tag_queries = "\n".join([
            f'node["{tag[0]}"="{tag[1]}"](around:{radius_m},{self.home_lat},{self.home_lng});'
            for tag in osm_tags
        ])
        
        query = f"""
[out:json][timeout:10];
(
  {tag_queries}
);
out body;
"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.OSM_OVERPASS_URL,
                data={"data": query},
                timeout=15
            )
        
        if response.status_code != 200:
            return []
        
        elements = response.json().get("elements", [])
        
        return [
            self._parse_osm_element(elem)
            for elem in elements
            if elem.get("tags", {}).get("name")  # Only named businesses
        ]
    
    def _parse_osm_element(self, element: dict) -> dict:
        tags = element.get("tags", {})
        lat = element.get("lat")
        lon = element.get("lon")
        
        distance = haversine_distance(
            self.home_lat, self.home_lng, lat, lon
        )
        
        return {
            "name": tags.get("name"),
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "address": tags.get("addr:housenumber", "") + " " + tags.get("addr:street", ""),
            "latitude": lat,
            "longitude": lon,
            "distance_meters": distance,
            "opening_hours": tags.get("opening_hours"),
            "source": "osm",
            "osm_id": element.get("id")
        }

# OSM tag mapping for Vietnamese household service categories
OSM_CATEGORY_TAGS = {
    "plumbing": [
        ("craft", "plumber"),
        ("shop", "plumber"),
        ("trade", "plumbing"),
    ],
    "electrical": [
        ("craft", "electrician"),
        ("shop", "electrical"),
        ("trade", "electrical"),
    ],
    "hvac": [
        ("craft", "hvac"),
        ("shop", "hvac"),
        ("service", "air_conditioning"),
    ],
    "appliance": [
        ("shop", "appliance_repair"),
        ("craft", "appliance_repair"),
        ("repair", "appliance"),
    ],
    "cleaning": [
        ("shop", "cleaning"),
        ("service", "cleaning"),
    ],
    "pest_control": [
        ("shop", "pest_control"),
        ("service", "pest_control"),
    ],
}

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates in meters."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
```

### 5.4 Message Drafter (`src/agents/message-drafter/`)

```python
# src/agents/message-drafter/drafter.py

class MessageDrafter:
    def __init__(self, claude_client: anthropic.Anthropic, db: aiosqlite.Connection):
        self.claude = claude_client
        self.db = db
    
    async def draft_service_request(
        self,
        issue_description: str,
        provider: ServiceProvider,
        available_times: list[str]  # ["sáng mai 8-10h", "chiều mai 2-4h"]
    ) -> str:
        """Draft a polite Vietnamese service request message."""
        
        # Privacy-safe context — no personal identifiers
        context = {
            "issue": issue_description,
            "provider": provider.name,
            "times": available_times[:3]  # Max 3 time options
        }
        
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": MESSAGE_DRAFT_PROMPT.format(**context)
            }]
        )
        
        draft = response.content[0].text.strip()
        
        # Save draft to DB
        await self.db.execute(
            """INSERT INTO message_log (provider_id, issue_description, draft_text, status)
               VALUES (?, ?, ?, 'draft')""",
            (provider.id, issue_description, draft)
        )
        
        return draft
    
    async def send_message(
        self, 
        message_id: int,
        final_text: str,
        channel: str,
        provider: ServiceProvider
    ) -> bool:
        """Send the confirmed message via the chosen channel."""
        
        success = False
        
        if channel == "sms" and self.twilio_client:
            success = await self._send_sms(provider.phone, final_text)
        elif channel == "zalo" and self.zalo_client:
            success = await self._send_zalo(provider.phone, final_text)
        elif channel == "clipboard":
            # Copy to clipboard — user sends manually
            import pyperclip
            pyperclip.copy(final_text)
            success = True
        
        # Update message log
        status = "sent" if success else "failed"
        await self.db.execute(
            """UPDATE message_log 
               SET final_text = ?, channel = ?, status = ?, sent_at = datetime('now')
               WHERE id = ?""",
            (final_text, channel, status, message_id)
        )
        
        return success

    def use_template_fallback(
        self, issue_description: str, provider_name: str
    ) -> str:
        """Fallback message template when Claude API is unavailable."""
        return (
            f"Xin chào {provider_name}, tôi cần {issue_description}. "
            f"Quý vị có thể sắp xếp thời gian không ạ? "
            f"Xin liên hệ lại để thống nhất. Cảm ơn!"
        )
```

---

## 6. Bill Processing Pipeline

### 6.1 Supported Vietnamese Bill Formats

| Issuer | Type | Common Formats | Extraction Confidence |
|--------|------|---------------|----------------------|
| EVN TP.HCM | Điện | Paper bill, SMS OTP notification, email | High (95%+) |
| EVN Hà Nội | Điện | Paper bill, app notification | High |
| SAWACO | Nước | Paper bill, SMS | High |
| Hà Nội Water | Nước | Paper bill | Medium |
| VNPT | Internet/Phone | Paper bill, email, SMS | High |
| Viettel | Phone/Internet | SMS, app, email | High |
| FPT Telecom | Internet | Email, paper | High |
| VCB/BIDV/TCB | Loan installment | SMS, email | Medium |
| Chủ nhà tư nhân | Rent | Handwritten, Zalo photo | Medium |

### 6.2 Bill State Machine

```
PENDING → (reminder sent) → REMINDED → (user marks paid) → PAID
                                      → (due date passed) → OVERDUE → (user marks paid) → PAID
                                                           → (7 days past due) → ALERT_FAMILY
```

### 6.3 Date Intelligence for Vietnamese Bills

```python
# Vietnamese date pattern variants found in bills
VIETNAMESE_DATE_PATTERNS = [
    r"(\d{2})/(\d{2})/(\d{4})",          # 15/06/2025
    r"ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})",  # ngày 15 tháng 6 năm 2025
    r"(\d{1,2})-(\d{2})-(\d{4})",         # 15-06-2025
    r"T(\d{1,2})/(\d{4})",                # T6/2025 (month/year for billing period)
    r"Tháng (\d{1,2})/(\d{4})",           # Tháng 6/2025
]
```

---

## 7. Service Finder — OSM + Places Integration

### 7.1 Search Strategy

```
User says: "Vòi nước bị hỏng"
  ↓
Issue classifier: category = "plumbing", urgency = "normal"
  ↓
Service finder:
  1. Check DB: any trusted plumbers cached?
     → If yes (trust_level ≥ 2): present trusted options first
  2. Search OSM Overpass API:
     → craft=plumber OR shop=plumber within 3km
  3. Sort results:
     Priority: trust_level DESC, rating DESC, distance ASC
  4. Present top 3-5 to user
  5. User selects one
  ↓
Message drafter creates service request
  ↓
User reviews and confirms
  ↓
Send via SMS/Zalo/clipboard
```

### 7.2 Provider Ranking Algorithm

```python
def rank_providers(providers: list[ServiceProvider]) -> list[ServiceProvider]:
    def score(p: ServiceProvider) -> float:
        # Trust level is most important (user's own experience wins)
        trust_score = p.trust_level * 30  # 0, 30, 60, or 90

        # Rating from public sources
        rating_score = (p.rating or 3.0) * 5  # 0-25

        # Prefer closer providers
        distance_penalty = min(p.distance_meters / 1000, 10) * 2  # 0-20

        # Freshness of data (cached data decays)
        freshness = 5 if p.source == "user_added" else 0

        return trust_score + rating_score - distance_penalty + freshness

    return sorted(providers, key=score, reverse=True)
```

### 7.3 Privacy-Safe Location Handling

```python
# Never send exact home address to external APIs
# Use bounding box or approximate center instead

def get_search_bounds(home_lat: float, home_lng: float, radius_km: float) -> dict:
    """Convert home coordinates to approximate bounding box for OSM search."""
    # 0.009 degrees ≈ 1km latitude
    delta = radius_km * 0.009
    return {
        "min_lat": home_lat - delta,
        "max_lat": home_lat + delta,
        "min_lng": home_lng - delta * 1.3,  # longitude correction
        "max_lng": home_lng + delta * 1.3,
    }

# The OSM query uses bounding box or 'around' (radius from approximate center)
# This gives ~100m precision, enough for search, not exact enough to reveal home
```

---

## 8. Reminder & Scheduling Engine

### 8.1 Reminder Configuration

```python
# User-configurable reminder schedule per bill type
DEFAULT_REMINDER_CONFIG = {
    "electricity": {"days_before": [5, 2, 0]},     # 5 days, 2 days, day-of
    "water":       {"days_before": [3, 1, 0]},
    "internet":    {"days_before": [5, 2]},
    "rent":        {"days_before": [7, 3, 1]},       # Rent gets more reminders
    "loan":        {"days_before": [7, 3, 1, 0]},    # Loan most critical
    "default":     {"days_before": [3, 1]},
}
```

### 8.2 Smart Scheduling — Avoid Inconvenient Times

```python
def adjust_reminder_time(scheduled: datetime) -> datetime:
    """Adjust reminders to be sent at appropriate times."""
    # Don't send at night
    if scheduled.hour < 7:
        return scheduled.replace(hour=8, minute=0)
    elif scheduled.hour >= 22:
        return (scheduled + timedelta(days=1)).replace(hour=8, minute=0)
    return scheduled
```

### 8.3 Maintenance Reminders

```python
def calculate_next_maintenance(item: MaintenanceItem) -> tuple[str, int | None]:
    """Calculate next service date and/or odometer."""
    
    next_date = None
    next_odo = None
    
    if item.interval_days and item.last_service_date:
        last = datetime.fromisoformat(item.last_service_date)
        next_date = (last + timedelta(days=item.interval_days)).isoformat()
    
    if item.interval_km and item.last_service_odometer:
        next_odo = item.last_service_odometer + item.interval_km
    
    # For "either whichever comes first" — schedule for the earlier of the two
    if next_date and next_odo and item.current_odometer:
        # If odometer already exceeds threshold, override date
        if item.current_odometer >= next_odo:
            next_date = datetime.now().isoformat()  # Overdue now
    
    return next_date, next_odo
```

---

## 9. Message Drafting Pipeline

### 9.1 Template Fallback System

For when the AI API is unavailable:

```python
MESSAGE_TEMPLATES = {
    "plumbing": "Xin chào {provider}, nhà tôi có {issue}. "
                "Quý vị có thể đến sửa giúp {time_options} được không? "
                "Xin liên hệ để thống nhất thêm. Cảm ơn!",
    
    "electrical": "Xin chào {provider}, nhà tôi bị sự cố điện: {issue}. "
                  "Quý vị có thể hỗ trợ {time_options} không ạ?",
    
    "hvac": "Xin chào {provider}, máy điều hòa nhà tôi cần {issue}. "
            "Quý vị có lịch {time_options} không ạ? Cảm ơn!",
    
    "default": "Xin chào {provider}, tôi cần {issue}. "
               "Thời gian thuận tiện: {time_options}. "
               "Mong phản hồi sớm. Cảm ơn!",
}
```

### 9.2 User Confirmation Flow

```
Draft generated
  ↓
Show to user:
  ┌────────────────────────────────┐
  │ Tin nhắn gửi cho Thợ Nguyễn   │
  │ SĐT: 0909 xxx xxx              │
  │                                │
  │ "Xin chào anh Nguyễn, nhà     │
  │  tôi bị hỏng vòi nước bếp.    │
  │  Anh có thể đến xem giúp      │
  │  sáng mai 8-10h hoặc chiều    │
  │  2-4h được không ạ?"          │
  │                                │
  │ [✏️ Sửa]  [📞 Gọi điện]        │
  │ [✅ Gửi SMS]  [📋 Sao chép]    │
  └────────────────────────────────┘
  ↓
User confirms → Message sent and logged
```

---

## 10. Expense Tracking & Reporting

### 10.1 Monthly Summary Generation

```python
async def generate_monthly_summary(year: int, month: int) -> dict:
    """Generate household expense summary for a given month."""
    
    # Query all paid bills for the month
    bills = await db.execute_many(
        """SELECT bill_type, SUM(paid_amount) as total, COUNT(*) as count
           FROM bills 
           WHERE strftime('%Y-%m', paid_date) = ?
           AND status = 'paid'
           GROUP BY bill_type""",
        (f"{year:04d}-{month:02d}",)
    )
    
    total = sum(b["total"] for b in bills)
    
    # Compare to same month last year
    last_year_total = await get_month_total(year - 1, month)
    yoy_change = ((total - last_year_total) / last_year_total * 100) if last_year_total else None
    
    return {
        "month": f"Tháng {month}/{year}",
        "total": total,
        "by_category": {b["bill_type"]: b["total"] for b in bills},
        "bill_count": sum(b["count"] for b in bills),
        "yoy_change_pct": yoy_change,
        "unpaid_count": await get_unpaid_count(year, month),
    }
```

### 10.2 Expense Report UI (Local Web Dashboard)

Simple charts using Chart.js (no cloud, renders locally):
- Monthly bar chart: expense by category
- 12-month trend line per utility
- Upcoming bills this month (calendar view)
- Overdue bills alert

---

## 11. Maintenance Tracker

### 11.1 Vietnamese Household Maintenance Templates

```python
MAINTENANCE_TEMPLATES = [
    # Vehicles
    {
        "name": "Xe máy — Thay nhớt",
        "type": "vehicle",
        "interval_days": 90,
        "interval_km": 3000,
        "notes": "Nhớt 4T, lọc nhớt (mỗi 2 lần thay), kiểm tra dây curoa, phanh"
    },
    {
        "name": "Xe máy — Bảo dưỡng tổng thể",
        "type": "vehicle",
        "interval_days": 180,
        "interval_km": 6000,
        "notes": "Thay bugi, kiểm tra hệ thống điện, lốp xe"
    },
    {
        "name": "Oto — Thay nhớt",
        "type": "vehicle",
        "interval_days": 90,
        "interval_km": 5000,
        "notes": "Nhớt động cơ, lọc nhớt, lọc gió"
    },
    
    # Home appliances
    {
        "name": "Điều hòa — Vệ sinh lọc bụi",
        "type": "appliance",
        "interval_days": 180,
        "notes": "Vệ sinh lưới lọc, kiểm tra gas nếu làm lạnh kém"
    },
    {
        "name": "Máy lọc nước — Thay lõi lọc",
        "type": "appliance",
        "interval_days": 180,
        "notes": "Lõi 1, 2, 3 — thay theo hướng dẫn nhà sản xuất"
    },
    {
        "name": "Bình đun nước nóng — Kiểm tra",
        "type": "appliance",
        "interval_days": 365,
        "notes": "Kiểm tra van áp lực, cặn trong bình, dây điện trở"
    },
    
    # Home systems
    {
        "name": "Bình chữa cháy — Kiểm tra",
        "type": "home_system",
        "interval_days": 365,
        "notes": "Kiểm tra áp suất đồng hồ, hạn sử dụng"
    },
    {
        "name": "Ống nước — Kiểm tra rò rỉ",
        "type": "home_system",
        "interval_days": 180,
        "notes": "Kiểm tra đồng hồ nước khi không dùng nước"
    },
]
```

---

## 12. Self-Learning Knowledge System

### 12.1 Knowledge Sources

| Source | Content | Update Frequency |
|--------|---------|-----------------|
| EVN website | Electricity billing format changes, new payment channels | Monthly |
| SAWACO/water companies | Water billing updates | Quarterly |
| VNPT/Viettel/FPT | Telecom billing format changes | Quarterly |
| OpenStreetMap | New local businesses added by community | Weekly (delta) |
| User feedback | "This provider was great/terrible" | Continuous |

### 12.2 Bill Format KB Entry

```yaml
# In SECOND-KNOWLEDGE-BRAIN.md
bill_formats:
  - issuer: "EVN TP.HCM"
    keywords: ["ĐIỆN LỰC", "EVN", "Hóa đơn tiền điện", "Chỉ số điện"]
    amount_field_patterns: 
      - "Số tiền phải trả.*?([0-9,\\.]+)\\s*đ"
      - "Tổng cộng.*?([0-9,\\.]+)"
    date_field_patterns:
      - "Ngày thanh toán.*?(\\d{2}/\\d{2}/\\d{4})"
      - "Hạn nộp.*?(\\d{2}/\\d{2}/\\d{4})"
    meter_number_pattern: "Số công tơ.*?(\\d{8,12})"
    last_updated: "2025-06-01"
    format_version: "2024_standard"
```

---

## 13. Privacy Architecture

### 13.1 Data Flow Audit

Every piece of family data classified and routed appropriately:

```
Data Type          | Stored In | Sent to Claude | Sent to OSM | Sent to Twilio
-------------------|-----------|----------------|-------------|----------------
Bill images        | Local     | ✅ (for OCR)   | ❌          | ❌
Bill amounts       | Local     | ❌             | ❌          | ❌
Account numbers    | Local     | ❌ (hidden)    | ❌          | ❌
Home address       | Local     | ❌             | ~approx     | ❌ (not in msg)
Family names       | Local     | ❌             | ❌          | ❌
Issue description  | Local     | ✅ (brief)     | ❌          | ❌
Provider name      | Local     | ✅             | ❌          | ❌
Message text       | Local     | ✅ (drafting)  | ❌          | ✅ (sending)
Expense totals     | Local     | ✅ (aggregate) | ❌          | ❌
```

### 13.2 SQLite Backup Strategy

```python
async def backup_database():
    """Daily backup of household data."""
    backup_dir = Path("data/backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"concierge_{timestamp}.db"
    
    # SQLite backup API (consistent copy even while DB is in use)
    source = sqlite3.connect("data/concierge.db")
    backup = sqlite3.connect(str(backup_path))
    source.backup(backup)
    backup.close()
    source.close()
    
    # Keep only last 7 backups
    old_backups = sorted(backup_dir.glob("*.db"))[:-7]
    for old in old_backups:
        old.unlink()
```

---

## 14. Performance Targets

| Metric | Target |
|--------|--------|
| Bill photo OCR → structured data | < 5 seconds |
| Nearby service search (OSM) | < 3 seconds |
| Message draft generation | < 3 seconds |
| Reminder notification delivery | < 1 second |
| App startup (React Native) | < 2 seconds |
| SQLite query response | < 100ms |
| Monthly expense report generation | < 2 seconds |
| Bill duplicate detection | < 200ms |
| Knowledge base update (weekly) | < 10 minutes |

---

## 15. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Bill photo OCR fails (poor photo quality) | Medium | Medium | Pre-processing + quality check + manual entry fallback |
| OSM lacks service providers in rural areas | High | Medium | Always show Google Maps fallback link; user can add providers manually |
| Vision API unavailable (network issue) | Low | Medium | EasyOCR local fallback; manual entry; cached bill formats |
| User accidentally confirms wrong message send | Low | Medium | 5-second undo window after confirmation |
| SQLite corruption | Very Low | High | Daily backups; WAL mode enabled; integrity check on startup |
| Service provider phone number outdated | Medium | Medium | "Provider didn't answer? Update or remove from list" flow |
| Bill format change breaks extraction | Medium | Medium | Weekly KB update catches format changes; manual override always available |
| Privacy: bill images contain account numbers | Medium | Medium | Documented accepted tradeoff; option to blur account numbers before sending to API |

---

## 16. Success Metrics

### Technical KPIs
- [ ] Bill OCR accuracy ≥ 92% on 20 test bill images (amount + due date)
- [ ] OSM search returns relevant results for 80%+ of service queries within 3km of city center
- [ ] Zero family data leaked to external services (security audit)

### User Experience KPIs
- [ ] Non-technical user adds and tracks first bill within 3 minutes of setup
- [ ] Reminder delivery ≤ 30 seconds of scheduled time
- [ ] "Service request sent" flow (issue → find → draft → confirm → send) completes in < 2 minutes
- [ ] Elderly user (65+) can review and confirm a drafted message without assistance

### Household Impact KPIs
- [ ] Zero overdue bills in test household after 3 months of use
- [ ] Monthly expense variance tracked within 5% accuracy vs manual tracking

---

*End of PROJECT-detail.md*
