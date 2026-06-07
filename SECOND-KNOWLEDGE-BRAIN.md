# SECOND-KNOWLEDGE-BRAIN.md

**The Living Knowledge Base of local-digital-concierge-agent**
Auto-updated by `knowledge-updater` | Version-controlled | Append-only
Last Crawl: 2025-06-01 | Total Entries: 24 (Initial Seed)

> **Scope**: Two knowledge categories: (1) Vietnamese Household Domain Knowledge — bill formats, utility companies, maintenance schedules specific to Vietnam; (2) Technical Research — local-first architecture, scheduling, OpenStreetMap integration, privacy-preserving AI patterns.

---

## Domain Keyword Index

**vietnamese utility bills**: [KB-2025-06-01-U001], [KB-2025-06-01-U002], [KB-2025-06-01-U003], [KB-2025-06-01-U004]
**local service providers**: [KB-2025-06-01-S001], [KB-2025-06-01-S002]
**vehicle maintenance vietnam**: [KB-2025-06-01-M001], [KB-2025-06-01-M002]
**home maintenance vietnam**: [KB-2025-06-01-M003]
**openstreetmap**: [KB-2025-06-01-T001], [KB-2025-06-01-T002]
**local-first architecture**: [KB-2025-06-01-T003], [KB-2025-06-01-T004]
**sqlite best practices**: [KB-2025-06-01-T005]
**apscheduler**: [KB-2025-06-01-T006]
**privacy-preserving ai**: [KB-2025-06-01-T007], [KB-2025-06-01-T008]
**ocr vietnamese**: [KB-2025-06-01-T009]
**household management ux**: [KB-2025-06-01-T010]
**payment methods vietnam**: [KB-2025-06-01-U005]

---

## ═══ SECTION 1: VIETNAMESE HOUSEHOLD DOMAIN KNOWLEDGE ═══

---

## [2025-06-01] [KB-2025-06-01-U001] Domain — EVN (Điện lực Việt Nam) — Bill Format & Payment Info

**Nguồn**: EVN official website + user research
**Domain**: [domain:electricity_bill]
**Applicability**: bill-processor, knowledge-updater

### Bill Identification Keywords
```
"ĐIỆN LỰC", "EVN", "Hóa đơn tiền điện", "Chỉ số điện", "Chỉ số kWh",
"CÔNG TY ĐIỆN LỰC", "TỔNG CÔNG TY ĐIỆN LỰC"
```

### Regional Companies
- **EVN TP.HCM** (EVNHCMC): Ho Chi Minh City
- **EVN Hà Nội** (EVNHANOI): Hanoi
- **EVN miền Trung** (EVNCPC): Central Vietnam
- **EVN miền Bắc** (EVNNPC): Northern provinces
- **EVN miền Nam** (EVNSPC): Southern provinces

### Bill Field Patterns (regex)
```python
PATTERNS = {
    "amount_due": [
        r"Số tiền phải trả[:\s]+([0-9,\.]+)\s*(?:đồng|đ|VNĐ)",
        r"TỔNG CỘNG[:\s]+([0-9,\.]+)",
        r"Tiền điện[:\s]+([0-9,\.]+)",
    ],
    "due_date": [
        r"(?:Hạn nộp|Ngày thanh toán)[:\s]+(\d{2}/\d{2}/\d{4})",
        r"(?:Thanh toán trước|Trước ngày)[:\s]+(\d{2}/\d{2}/\d{4})",
    ],
    "meter_number": [
        r"Số công tơ[:\s]+(\d{8,12})",
        r"Mã công tơ[:\s]+(\d{8,12})",
        r"Mã KH[:\s]+(\d{8,14})",
    ],
    "billing_period": [
        r"Kỳ tính điện[:\s]+(\d{2}/\d{4})\s*(?:đến|→|-)\s*(\d{2}/\d{4})",
        r"Từ (\d{2}/\d{2}/\d{4})\s*đến\s*(\d{2}/\d{2}/\d{4})",
    ]
}
```

### Payment Methods (current as of 2025)
- Ứng dụng EVNHCMC trên điện thoại
- Ngân hàng: chuyển khoản / ATM / Internet Banking / Mobile Banking (tất cả ngân hàng lớn)
- ViettelPay, MoMo, ZaloPay, VNPay, Moca
- Thu ngân tại bưu điện (Bưu điện Việt Nam)
- Thu ngân EVN (phòng giao dịch)
- Thanh toán tiền mặt tại siêu thị CoopMart, BigC

### Billing Cycle
- Hàng tháng (đọc chỉ số ngày cố định hàng tháng)
- Due date: thường 15-20 ngày sau ngày in hóa đơn

### Citation
`EVN HCMC. (2025). Hướng dẫn thanh toán tiền điện. evnhcmc.vn`

---

## [2025-06-01] [KB-2025-06-01-U002] Domain — SAWACO & Công ty Nước — Bill Format

**Nguồn**: SAWACO official + various water company data
**Domain**: [domain:water_bill]

### Vietnamese Water Companies
- **SAWACO**: TP.HCM — Tổng Công ty Cấp nước Sài Gòn
- **HAWACOM**: Hà Nội — Công ty TNHH MTV Nước sạch Hà Nội
- **Cấp nước Đà Nẵng**: Đà Nẵng

### Bill Identification Keywords
```
"CẤP NƯỚC", "SAWACO", "HÓA ĐƠN TIỀN NƯỚC", "Chỉ số nước",
"m³", "Mét khối", "CÔNG TY CẤP NƯỚC"
```

### Key Field Patterns
```python
SAWACO_PATTERNS = {
    "amount_due": r"Tiền nước[:\s]+([0-9,\.]+)",
    "due_date": r"Hạn thu(?:ế)?[:\s]+(\d{2}/\d{2}/\d{4})",
    "meter_id": r"Mã đồng hồ[:\s]+(\d{6,12})",
    "usage_m3": r"Sản lượng[:\s]+(\d+)\s*m³",
}
```

### Common Billing Issues Users Ask About
- "Tiền nước tháng này sao cao hơn?" → leakage detection tip: check meter when not using water
- "Bị tính hai lần" → contact SAWACO hotline: 1800 599 927 (free, 24/7)

### Citation
`SAWACO. (2025). Thông tin hóa đơn. sawaco.com.vn`

---

## [2025-06-01] [KB-2025-06-01-U003] Domain — VNPT / Viettel / FPT — Telecom Bill Formats

**Domain**: [domain:internet_phone_bill]

### Internet + Phone Bill Keywords
```
VNPT: "VNPT", "Bưu chính Viễn thông", "Tập đoàn Bưu chính Viễn thông"
Viettel: "VIETTEL", "Tập đoàn Công nghiệp Viễn thông Quân đội"
FPT: "FPT Telecom", "Công ty Cổ phần Viễn thông FPT"
```

### Amount Due Patterns
```python
TELECOM_PATTERNS = {
    "amount_due": [
        r"Tổng cước phí[:\s]+([0-9,\.]+)",
        r"Số tiền thanh toán[:\s]+([0-9,\.]+)",
        r"Cước phải thanh toán[:\s]+([0-9,\.]+)",
    ],
    "due_date": [
        r"Hạn thanh toán[:\s]+(\d{2}/\d{2}/\d{4})",
        r"Vui lòng thanh toán trước[:\s]+(\d{2}/\d{2}/\d{4})",
    ],
    "account_id": [
        r"Mã khách hàng[:\s]+(\d{8,14})",
        r"Số hợp đồng[:\s]+(\w{8,16})",
    ]
}
```

### Late Payment Consequences
- VNPT: Tạm ngừng dịch vụ sau 30 ngày quá hạn
- Viettel: Khóa dịch vụ sau 15 ngày quá hạn
- FPT: Khóa sau 30 ngày; hủy hợp đồng sau 90 ngày

### Citation
`VNPT, Viettel, FPT official websites. (2025). Hướng dẫn thanh toán.`

---

## [2025-06-01] [KB-2025-06-01-U004] Domain — Hóa đơn thuê nhà (Rent Invoice)

**Domain**: [domain:rent_bill]

### Common Rent Invoice Formats
Unlike utility bills (which have standard formats), rent invoices in Vietnam are often:
- Handwritten on plain paper
- Sent via Zalo photo message
- Simple table: "Tiền thuê tháng X: Y đồng"

### Key Fields to Extract
```python
RENT_PATTERNS = {
    "amount_due": [
        r"(?:Tiền thuê|Tiền nhà|Tiền trọ)[:\s]+([0-9,\.]+)",
        r"Tháng \d+[:\s]+([0-9,\.]+)",
    ],
    "due_date": [
        r"(?:Đóng trước|Hạn nộp|Ngày)[:\s]+(\d{1,2})[/\s](\d{1,2})[/\s](\d{4})",
        r"Thanh toán ngày (\d{1,2}) hàng tháng",  # "Thanh toán ngày 5 hàng tháng"
    ],
    "period": r"[Tt]háng (\d{1,2})/(\d{4})"
}
```

### Unusual Rent Extraction Handling
- "Thanh toán ngày 5 hàng tháng" → calculate next 5th of current or next month
- Handwritten amounts may have dots as thousands separator: "5.000.000" or "5,000,000"

---

## [2025-06-01] [KB-2025-06-01-U005] Domain — Phương thức thanh toán hóa đơn tại Việt Nam 2025

**Domain**: [domain:payment_methods]

### Digital Payment Methods (phổ biến nhất 2025)
1. **MoMo** (market leader): Quét mã QR hóa đơn → thanh toán tức thì
2. **ZaloPay**: Tích hợp trong Zalo, quét mã QR hoặc chuyển khoản
3. **VNPay** (QR): Hầu hết ngân hàng hỗ trợ, phổ biến ở siêu thị/cửa hàng
4. **Ngân hàng Internet Banking**: Chuyển khoản thủ công theo số tài khoản

### Physical Payment Methods
- **Bưu điện Việt Nam**: Thanh toán tại quầy, nhân viên thu tại nhà (vùng nông thôn)
- **Siêu thị**: CoopMart, Winmart, BigC có quầy thu hộ tiện ích
- **Convenience stores**: GS25, 7-Eleven, Circle K (đang mở rộng)

### QR Code Bill Payment (growing trend)
- EVN, SAWACO, VNPT đều in QR code trên hóa đơn 2024+
- Applicability: khi extract hóa đơn có QR code → gợi ý "Quét mã này bằng MoMo/ZaloPay để thanh toán nhanh"

---

## [2025-06-01] [KB-2025-06-01-S001] Domain — Dịch vụ sửa chữa nhà tại Việt Nam — Cách tìm

**Domain**: [domain:home_services]

### How Vietnamese Households Find Repairmen (research 2024)
1. **Zalo/Facebook neighborhood groups** (most trusted): "Hội cư dân Quận 7", "Cư dân Vinhomes"
2. **Word-of-mouth from neighbors**: highest trust, limited reach
3. **Stickers on walls/poles**: thợ điện nước dán số điện thoại
4. **Online platforms**: BTaskee, GrabExpress (limited areas), JupViec

### Service Categories Common in Vietnamese Households
```python
VIETNAMESE_SERVICE_KEYWORDS = {
    "plumbing": ["thợ sửa ống nước", "thợ vệ sinh môi trường", "thợ sửa đường ống",
                 "sửa vòi nước", "thông cống", "sửa bồn cầu", "thợ cấp thoát nước"],
    "electrical": ["thợ điện", "sửa điện", "lắp đặt điện", "thợ điện nước"],
    "hvac": ["sửa máy lạnh", "vệ sinh máy lạnh", "nạp gas điều hòa", "sửa điều hòa"],
    "appliance": ["sửa tủ lạnh", "sửa máy giặt", "sửa máy bơm nước", "sửa lò vi sóng"],
    "structural": ["thợ xây", "thợ sơn", "sửa mái nhà", "thợ lát gạch"],
    "pest_control": ["diệt mối mọt", "diệt muỗi", "diệt gián", "phun thuốc"],
    "cleaning": ["dọn nhà", "vệ sinh công nghiệp", "giúp việc theo giờ"],
}
```

### OSM Tags for Vietnamese Service Businesses
Many Vietnamese service businesses are NOT on OSM yet (esp. small local shops). Strategy:
1. Search OSM for what's there (craft=plumber etc.)
2. Show Google Maps fallback link for full coverage: `https://maps.google.com?q=thợ+sửa+nước+near+me`
3. Let users add their trusted providers manually (most valuable source)

---

## [2025-06-01] [KB-2025-06-01-S002] Domain — Bảng giá dịch vụ sửa chữa điển hình TP.HCM 2025

**Domain**: [domain:home_services]
**Applicability**: service-finder (helps validate if quoted price is reasonable)

### Typical Service Costs (TP.HCM, 2025 estimate)
- Sửa vòi nước hỏng đơn giản: 100.000–300.000 đ
- Thông cống bồn rửa: 150.000–400.000 đ
- Sửa bồn cầu: 200.000–500.000 đ
- Thay đường ống nước mới (5m): 500.000–1.500.000 đ
- Sửa ổ điện/công tắc: 100.000–250.000 đ
- Thay bóng đèn LED âm trần: 50.000–150.000 đ/bóng
- Vệ sinh máy lạnh 1 cục: 150.000–350.000 đ
- Nạp gas điều hòa: 200.000–500.000 đ
- Sơn lại 1 phòng (~20m²): 1.500.000–3.000.000 đ

Note: Prices for emergency/night calls typically 1.5-2x above

---

## [2025-06-01] [KB-2025-06-01-M001] Domain — Xe máy — Lịch bảo dưỡng tại Việt Nam

**Domain**: [domain:vehicle_maintenance]

### Standard Maintenance Intervals for Common Vietnamese Motorbikes
```python
MOTORBIKE_SCHEDULES = {
    "Honda Wave/Future/Blade": {
        "oil_change": {"km": 3000, "months": 3},
        "air_filter": {"km": 12000, "months": 12},
        "spark_plug": {"km": 12000, "months": 12},
        "drive_belt": {"km": 20000, "months": 24},   # Xe số tự động
        "brake_pads": {"km": 15000, "advice": "check every service"},
    },
    "Honda SH/PCX/Air Blade": {  # xe ga
        "oil_change": {"km": 3000, "months": 3},
        "air_filter": {"km": 8000, "months": 6},
        "spark_plug": {"km": 12000, "months": 12},
        "drive_belt": {"km": 25000, "months": 24},
        "roller_weights": {"km": 25000},
    },
    "Yamaha NVX/Exciter/Acruzo": {
        "oil_change": {"km": 3000, "months": 3},
        "air_filter": {"km": 8000, "months": 12},
        "spark_plug": {"km": 12000, "months": 12},
    },
    "Suzuki GSX/Raider": {
        "oil_change": {"km": 3000, "months": 3},
        "spark_plug": {"km": 12000, "months": 12},
    }
}
```

### Where to Get Serviced in Vietnam
- **Hãng chính thức (Head)**: Honda HEAD, Yamaha TownTeam — authorized, quality guaranteed, slightly expensive
- **Thợ bên đường/tiệm sửa xe**: Much cheaper, quality varies widely
- **Recommendation to users**: For xe máy, authorized service center for major repairs; roadside for oil change is fine

### Oil Types Common in Vietnam
- Nhớt khoáng (mineral): Honda Motor Oil 10W-30 — cheapest, change more frequently
- Nhớt tổng hợp (synthetic): Motul, Shell, Castrol — better, change every 4000-5000km
- Note for extraction: if user says "thay dầu" or "thay nhớt" — same thing

---

## [2025-06-01] [KB-2025-06-01-M002] Domain — Oto — Lịch bảo dưỡng tại Việt Nam

**Domain**: [domain:vehicle_maintenance]

### Standard Car Maintenance Schedule (Vietnam conditions)
Vietnam's road conditions (dust, heat, traffic jams) require more frequent service than European/American recommendations.

```python
CAR_MAINTENANCE_VN = {
    "oil_change": {
        "mineral_oil": {"km": 5000, "months": 6},
        "synthetic_oil": {"km": 8000, "months": 6},
        "default": {"km": 5000, "months": 6},  # Conservative for VN conditions
    },
    "air_filter": {"km": 15000, "months": 12},
    "cabin_filter": {"km": 15000, "months": 12},
    "fuel_filter": {"km": 30000, "months": 24},
    "brake_fluid": {"km": 40000, "months": 24},
    "coolant": {"km": 40000, "months": 24},
    "spark_plugs_iridium": {"km": 100000},
    "timing_belt": {"km": 80000, "advice": "check manual for your model"},
    "annual_inspection": {"months": 12, "note": "đăng kiểm bắt buộc"},
}
```

### Vietnamese Vehicle Registration (Đăng kiểm) — Legal Requirement
- Xe oto dưới 7 chỗ ngồi: đăng kiểm mỗi 12 tháng
- Reminder should be set 30 days before registration expiry
- Penalty: phạt tiền 300.000-400.000đ nếu quá hạn đăng kiểm

---

## [2025-06-01] [KB-2025-06-01-M003] Domain — Thiết bị gia đình — Lịch bảo dưỡng

**Domain**: [domain:home_maintenance]

### Standard Home Appliance Maintenance (Vietnam)
```python
HOME_APPLIANCE_SCHEDULE = {
    "air_conditioner_filter_clean": {
        "months": 3,      # Trong môi trường bụi VN, rửa lọc mỗi 3 tháng
        "service_clean": {"months": 12},  # Vệ sinh chuyên sâu mỗi năm
        "gas_refill_check": {"months": 24},  # Kiểm tra gas nếu làm lạnh kém
    },
    "water_purifier_filter": {
        "filter_1": {"months": 3},     # Lõi thô (sediment)
        "filter_2_3": {"months": 6},   # Lõi UDF/GAC
        "filter_ro": {"months": 18},   # Lõi RO (đắt nhất)
        "uv_lamp": {"months": 12},     # Đèn UV (nếu có)
    },
    "water_heater": {
        "flush_sediment": {"months": 12},
        "pressure_valve_check": {"months": 12},
        "full_service": {"months": 24},
    },
    "fire_extinguisher": {
        "visual_check": {"months": 6},
        "professional_check": {"months": 12},
        "refill_or_replace": {"years": 5},
    },
    "washing_machine": {
        "drum_clean": {"months": 1},   # Chạy chế độ vệ sinh lồng giặt hàng tháng
        "filter_clean": {"months": 3}, # Lọc cặn (nếu có)
    }
}
```

### Vietnamese Seasonal Maintenance Notes
- **Mùa mưa (tháng 5-11 TP.HCM)**: Kiểm tra mái nhà, máng xối trước mùa mưa (tháng 4)
- **Trước Tết**: Vệ sinh tổng thể, sơn phết, sửa chữa nhỏ (thường tháng 12-1)
- **Mùa nóng (tháng 3-4)**: Kiểm tra máy lạnh, máy bơm nước

---

## ═══ SECTION 2: TECHNICAL RESEARCH ═══

---

## [2025-06-01] [KB-2025-06-01-T001] Technical — OpenStreetMap Overpass API — Best Practices

**Source**: OSM Wiki + Overpass API documentation
**URL**: https://wiki.openstreetmap.org/wiki/Overpass_API
**Relevance Score**: 1.0
**Categories**: service-finder

### Key Facts
- Overpass API is free to use (rate limit: be polite — max 1 request/second for automated queries)
- Main endpoint: `https://overpass-api.de/api/interpreter`
- Alternative mirrors: `https://overpass.kumi.systems`, `https://overpass.openstreetmap.ru`
- Response format: JSON or XML

### Optimal Query Strategy for Service Providers
```
[out:json][timeout:10];
(
  node["craft"="plumber"](around:3000,10.7769,106.7009);
  node["shop"="plumber"](around:3000,10.7769,106.7009);
  way["craft"="plumber"](around:3000,10.7769,106.7009);
);
out body;
```

### Vietnamese Business Tags on OSM
OSM data quality in Vietnam is moderate — major cities have good coverage, rural areas sparse.
- Many Vietnamese businesses use: `name:vi` for Vietnamese name, `name:en` for English
- Phone numbers may be in `phone`, `contact:phone`, or `contact:mobile`
- Opening hours in `opening_hours` tag (standard OSM format)

### Privacy Note
- Using `around:radius,lat,lng` in Overpass query: the exact coordinates are sent to OSM servers
- Use a slightly randomized center point (±200m) to avoid revealing exact home address to OSM
- OSM is privacy-friendly (open data, no user tracking) but this extra step is good practice

### Applicability
- `ServiceFinder._search_osm()` implementation
- Always include multiple tag variants for same service type (craft AND shop AND service)

### Citation
`OpenStreetMap Wiki. (2024). Overpass API. wiki.openstreetmap.org/wiki/Overpass_API`

---

## [2025-06-01] [KB-2025-06-01-T003] Technical — Local-First Software Architecture

**Authors**: Kleppmann, M. et al. (Ink & Switch Research)
**Source**: "Local-First Software" (2019) + CRDTs for Offline
**URL**: https://www.inkandswitch.com/local-first/
**Relevance Score**: 0.97
**Categories**: orchestrator, database

### Summary
The "Local-First Software" manifesto defines a set of principles for software that respects user agency and works offline. Core principle: the primary copy of data lives on the user's device, not on vendor servers. The paper identifies 7 ideals: no spinners, work is not trapped on one device, network is optional, collaborating with others, long-now access (data accessible in 10+ years), security and privacy, user is in control.

### Key Findings
- **SQLite is the correct local-first database**: single file, portable, zero config, works offline
- **Conflict-free for single-household**: since one household uses one device primarily, CRDTs (complex distributed data structures) are unnecessary — simple SQLite is sufficient
- **Local-first ≠ no cloud**: local-first means the local copy is authoritative; sync to cloud is optional backup
- **Long-term data viability**: SQLite database from 2005 is still readable today — better longevity than cloud service accounts

### Applicability
- Validates SQLite choice over Firebase/Supabase
- Offline capability is a feature, not an afterthought
- Data portability: users can copy `concierge.db` and open it with any SQLite tool — no lock-in

### Citation
`Kleppmann, M. et al. (2019). Local-First Software: You Own Your Data, in Spite of the Cloud. inkandswitch.com/local-first/`

---

## [2025-06-01] [KB-2025-06-01-T004] Technical — SQLite for Production Applications

**Source**: SQLite official documentation + Litestream + Turso
**URL**: https://sqlite.org/whentouse.html
**Relevance Score**: 0.95
**Categories**: database

### Key Findings
- SQLite handles up to **100,000 transactions/day** comfortably — far more than any household needs
- **WAL mode** (`PRAGMA journal_mode=WAL`): enables concurrent reads while writing; 5-10x faster for mixed workload
- **VACUUM** should be run monthly to reclaim space from deleted records
- SQLite file size for 10 years of household data (1000 bills/year): ~50MB
- `PRAGMA integrity_check`: run on startup to detect corruption

### Best Practices for This Project
```python
async def initialize_db(db_path: str) -> aiosqlite.Connection:
    conn = await aiosqlite.connect(db_path)
    
    # Performance + safety settings
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA synchronous=NORMAL")  # Faster, safe with WAL
    await conn.execute("PRAGMA foreign_keys=ON")     # Enforce FK constraints
    await conn.execute("PRAGMA cache_size=10000")    # 10MB page cache
    
    # Integrity check on startup
    result = await conn.execute_fetchall("PRAGMA integrity_check")
    if result[0][0] != "ok":
        raise DatabaseCorruptionError("Database integrity check failed")
    
    return conn
```

### Applicability
- `src/database/db_client.py` initialization sequence
- WAL mode is non-negotiable for this project (reminders + user interaction run concurrently)

### Citation
`SQLite Documentation. (2024). When to use SQLite. sqlite.org/whentouse.html`

---

## [2025-06-01] [KB-2025-06-01-T005] Technical — APScheduler for Python Local Scheduling

**Source**: APScheduler documentation
**URL**: https://apscheduler.readthedocs.io/en/stable/
**Relevance Score**: 0.97
**Categories**: scheduler

### Why APScheduler Over Alternatives

| Tool | Why Not |
|------|---------|
| Cron | Doesn't run on Windows; no persistent job state; hard to manage from Python |
| Celery | Requires Redis/RabbitMQ; overkill for household; complex setup |
| Cloud task queues | Privacy concern; requires internet; vendor lock-in |
| APScheduler | In-process Python, persistent SQLite job store, works everywhere, simple API |

### Key Configuration for This Project
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

scheduler = AsyncIOScheduler(
    jobstores={
        "default": SQLAlchemyJobStore(
            url="sqlite:///data/concierge.db",
            tablename="apscheduler_jobs"
        )
    },
    job_defaults={
        "coalesce": True,           # If missed (system off), run once on wake
        "max_instances": 1,         # Don't run same job twice simultaneously
        "misfire_grace_time": 3600, # Run if up to 1 hour late (system was off)
    },
    timezone="Asia/Ho_Chi_Minh"
)
```

### Critical: `misfire_grace_time`
If the device is turned off when a reminder should fire, APScheduler will fire the reminder when the device turns back on (within the grace period). For household reminders, 1 hour grace is appropriate.

### Applicability
- `ReminderEngine.__init__()` configuration
- Store APScheduler jobs in the SAME SQLite database as household data (one file!)

### Citation
`APScheduler Documentation. (2024). apscheduler.readthedocs.io`

---

## [2025-06-01] [KB-2025-06-01-T006] Technical — ntfy.sh for Self-Hosted Push Notifications

**Source**: ntfy.sh official documentation
**URL**: https://docs.ntfy.sh/
**Relevance Score**: 0.92
**Categories**: scheduler, notifications

### Why ntfy for This Project
- **Self-hostable**: Can run on the same Raspberry Pi as the agent (no cloud dependency)
- **No account needed**: Use ntfy.sh free tier OR self-host
- **Multi-platform**: Push to Android, iOS (via ntfy app), web browser
- **Simple API**: HTTP POST to send notification

```python
import httpx

async def send_ntfy_notification(
    topic: str,         # Unique to this household (random UUID)
    title: str,
    message: str,
    priority: int = 3   # 1-5, 5 is urgent
):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://ntfy.sh/{topic}",  # Or self-hosted URL
            data=message.encode(),
            headers={
                "Title": title,
                "Priority": str(priority),
                "Tags": "bell",
            }
        )
```

### Privacy Note
If using ntfy.sh (cloud), notification content is transmitted to ntfy servers.
For full privacy: self-host ntfy on Raspberry Pi. Setup: `docker run -p 80:80 binwiederhier/ntfy serve`

### Applicability
- `src/tools/notification_manager.py` primary implementation
- Document both cloud and self-hosted options in setup guide

### Citation
`ntfy.sh. (2024). Documentation. docs.ntfy.sh`

---

## [2025-06-01] [KB-2025-06-01-T007] Technical — Privacy-Preserving AI API Integration

**Source**: Anthropic Privacy Best Practices + Research
**Relevance Score**: 1.0
**Categories**: llm-client, privacy

### Minimum Data Principle for AI API Calls
Best practice: send only what the AI model absolutely needs to complete the task.

```python
# For bill extraction: send the image only
# The image DOES contain account numbers — this is an accepted tradeoff
# for OCR accuracy. Document this clearly for users.

# For message drafting: send the minimum context
SAFE_CONTEXT = {
    "issue": "vòi nước bị hỏng",        # Issue type (no location)
    "provider": "Thợ Nguyễn Văn A",     # Provider first name only
    "times": ["sáng mai", "chiều mai"],  # Time preferences (not exact schedule)
    # NOT included:
    # - home address
    # - family name
    # - phone numbers
    # - bill amounts
    # - account numbers
}

# For monthly summary: aggregate only
SAFE_SUMMARY_CONTEXT = {
    "electricity_total": 450000,   # Aggregated, not individual bills
    "water_total": 120000,
    "internet_total": 280000,
    # NOT included: specific bill dates, account numbers, payment history
}
```

### Applicability
- `src/tools/llm_client.py` — enforce minimum data principle as code review checklist
- All API call contexts must be reviewed against this pattern

### Citation
`Anthropic. (2024). Model Specification. Privacy and data handling principles.`

---

## [2025-06-01] [KB-2025-06-01-T008] Technical — EasyOCR Vietnamese Performance

**Source**: EasyOCR documentation + community benchmarks
**URL**: https://github.com/JaidedAI/EasyOCR
**Relevance Score**: 0.90
**Categories**: bill-processor (offline fallback)

### Vietnamese OCR Performance
- EasyOCR with ['vi', 'en'] languages: ~85% accuracy on clear printed Vietnamese text
- Common failure points: tone mark confusion (à/á/ả/ã/ạ), numbers in tables
- Improvement: pre-process image (contrast enhancement) before EasyOCR = +5-8% accuracy

### Setup for This Project
```python
# One-time initialization (takes 5-10 seconds to load models)
import easyocr
reader = easyocr.Reader(['vi', 'en'], gpu=False)  # CPU-only for Raspberry Pi

# Usage
results = reader.readtext(image_bytes, detail=0, paragraph=True)
# Returns list of text strings
full_text = " ".join(results)
```

### Regex Post-Processing Critical for Vietnamese Bills
After EasyOCR, numbers in bills often have OCR errors:
- "5.000.000" might be read as "5,000,000" or "5 000 000" → normalize all to integer
- Letters confused in amounts: "0" vs "O", "1" vs "l" → validate with regex

### Applicability
- `FallbackOCR` class in `src/agents/bill-processor/processor.py`
- Initialize EasyOCR at agent startup (slow) not per-request

### Citation
`Kittinaradorn, R. (2024). EasyOCR. github.com/JaidedAI/EasyOCR`

---

## [2025-06-01] [KB-2025-06-01-T009] Technical — Vietnamese Date and Number Parsing

**Source**: Python community + Vietnamese locale research
**Relevance Score**: 0.95
**Categories**: bill-processor

### Vietnamese Date Formats to Handle
```python
VIETNAMESE_DATE_PATTERNS = {
    # Standard formats
    "dd/MM/yyyy": r"(\d{1,2})/(\d{1,2})/(\d{4})",
    "dd-MM-yyyy": r"(\d{1,2})-(\d{1,2})-(\d{4})",
    
    # Written out
    "ngay_thang_nam": r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",
    "thang_nam_only": r"[Tt]háng\s+(\d{1,2})[/\-](\d{4})",  # "Tháng 6/2025"
    
    # Relative (need to resolve at runtime)
    "relative": {
        "hôm nay": lambda: date.today(),
        "ngày mai": lambda: date.today() + timedelta(days=1),
        "đầu tháng": lambda: date.today().replace(day=1),
        "cuối tháng": lambda: last_day_of_month(date.today()),
        "ngày {d} hàng tháng": lambda d: next_occurrence_of_day(int(d)),
    }
}
```

### Vietnamese Number Formats
```python
def parse_vietnamese_number(text: str) -> int:
    """Parse Vietnamese number formats to integer."""
    # Remove dots (thousands separator in Vietnamese)
    text = re.sub(r'\.(?=\d{3})', '', text)
    # Remove commas (also used as thousands separator)
    text = text.replace(',', '')
    # Handle "triệu" (million) and "nghìn/ngàn" (thousand) words
    text = re.sub(r'(\d+)\s*triệu', lambda m: str(int(m.group(1)) * 1_000_000), text)
    text = re.sub(r'(\d+)\s*(?:nghìn|ngàn)', lambda m: str(int(m.group(1)) * 1_000), text)
    return int(re.sub(r'[^\d]', '', text))
```

### Applicability
- `src/agents/bill-processor/processor.py` validation step
- `src/agents/message-drafter/drafter.py` for time slot parsing

---

## [2025-06-01] [KB-2025-06-01-T010] Research — UX for Non-Technical Household Users

**Source**: Nielsen Norman Group + Vietnamese UX research
**Relevance Score**: 0.93
**Categories**: mobile-app, web-dashboard

### Key UX Principles for Non-Technical Vietnamese Households

**1. Camera-First Input (not form-first)**
Non-technical users are MUCH more comfortable taking a photo than filling a form. Design: photo first → agent extracts → user confirms. NEVER show a form as the primary interface.

**2. Vietnamese Number Formatting in UI**
- Always display: 1.234.567 đ (dot as thousands separator, Vietnamese convention)
- NOT: 1,234,567 VND (English convention confuses Vietnamese users)
- Shorthand acceptable for large numbers: "12 triệu 5" for 12,500,000

**3. Confirmation Before Action Pattern**
Vietnamese users (esp. older) deeply dislike unexpected actions. ALWAYS preview:
- "Tôi sẽ làm X. Bạn có đồng ý không?" before any action
- 5-second undo for sent messages

**4. Household Member Trust Hierarchy**
In Vietnamese households, typically one "manager" (often wife/mother) is primary user. Design for this: one primary user manages all settings, others can view and acknowledge reminders.

**5. Success Feedback (Positive Reinforcement)**
"✅ Đã ghi nhớ hóa đơn điện tháng 6. Nhắc nhở sẽ đến 12/6." — users need to know things worked.

### Citation
`Nielsen Norman Group. (2023). Designing for Low-Tech Users. nngroup.com`

---

## 📅 Update Log

| Date | Entries Added | Sources | Triggered By |
|------|--------------|---------|-------------|
| 2025-06-01 | 24 (initial seed) | EVN/SAWACO/VNPT official sites, OSM docs, SQLite docs, APScheduler, technical research | Project initialization |

---

## 🔍 Upcoming Crawl Targets

- [ ] EVN HCMC billing format changes (evnhcmc.vn)
- [ ] SAWACO new payment methods
- [ ] OSM Vietnam community — new business categories
- [ ] ntfy.sh new features
- [ ] APScheduler 3.x release notes
- [ ] New Vietnamese payment platforms (check for new apps)

---

*Append-only. Tagged: [domain:electricity_bill], [domain:water_bill], [domain:internet_phone_bill], [domain:rent_bill], [domain:vehicle_maintenance], [domain:home_maintenance], [domain:home_services], [technical:sqlite], [technical:apscheduler], [technical:osm], [technical:privacy]*
