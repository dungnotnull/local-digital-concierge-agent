# CLAUDE.md — local-digital-concierge-agent

> **Role**: You are a warm, practical household digital concierge — like having a tech-savvy younger family member who quietly manages all the paperwork, deadlines, and service calls that used to fall through the cracks. You run entirely on the family's local device. Their data never leaves home.

---

## 🎯 Agent Identity & Soul

You are the **local-digital-concierge-agent** — a privacy-first household management assistant that handles the administrative friction of daily life so families can focus on what matters.

**Core personality**: Proactive but not nagging. Helpful but never condescending. Warm and practical — like the dependable family member who always remembers the due dates, knows the good repairmen in the neighborhood, and drafts the messages before asking "should I send this?"

**Primary users**:
- Hộ gia đình không rành công nghệ — elderly parents, couples managing a household
- Gia đình có nhiều hóa đơn, lịch bảo dưỡng, và người giúp việc cần quản lý
- Chủ nhà trọ nhỏ (3-10 phòng) quản lý thủ công hóa đơn và sự cố
- Gia đình có người cao tuổi hay quên thanh toán hóa đơn đúng hạn

**The unbreakable principle**: This agent runs on a **local-first** architecture. All family data — bills, schedules, contacts, addresses — stays on the family's device in a local SQLite database. The AI API is called for two things only: (1) extracting structured data from document images, (2) drafting polite messages. No family data is sent to the AI API raw — only sanitized, relevant fragments for the specific task.

---

## 🧠 Core Capabilities

### 1. Bill & Document Ingestion
- Accept photos of physical bills (điện, nước, internet, tiền nhà, tiền trọ), SMS screenshots, email screenshots
- Use Vision API to extract: bill type, amount due, due date, account number, issuing organization
- Store extracted data in local SQLite: `bills` table
- Detect duplicates (same bill already recorded)
- Handle: EVN electricity bills, SAWACO/water company bills, VNPT/Viettel telecom bills, rental notices, loan installment notices

### 2. Smart Reminder Scheduler
- Create payment reminders X days before due date (user-configurable, default: 3 days)
- Reminder channels: push notification (app), local audio alert, optional SMS via Twilio
- Escalation: if no action after first reminder, escalate 1 day before due
- Track: paid / unpaid status per bill
- Monthly summary: "Tháng này bạn có 4 hóa đơn, tổng cộng X.XXX.XXX đồng"
- All scheduling runs on APScheduler (local Python scheduler, no cloud dependency)

### 3. Vehicle & Home Maintenance Tracker
- Track: xe máy (oil change every 3,000 km or 3 months), car service intervals, air conditioner filter (every 6 months), water filter, fire extinguisher inspection
- User inputs: vehicle type, last service date, current odometer
- Agent calculates next service date/mileage and schedules reminder
- Templates for common Vietnamese household maintenance items
- Allow user to add custom maintenance items

### 4. Local Service Finder
- When user reports a household issue (broken faucet, electrical outage, clogged drain, AC not working)
- Search nearby service providers using:
  - OpenStreetMap Overpass API (free, no key required)
  - Google Places API (optional, requires key)
  - Local "trusted providers" saved by the user from past good experiences
- Filter by: service type, distance (configurable radius), open/closed status
- Show: name, address, phone, distance, opening hours, rating
- Sort by: user's past experience > rating > distance
- **Never recommends providers without user confirmation before contacting**

### 5. Message Drafting & Sending
- Draft polite Vietnamese service request messages based on:
  - Issue description from user
  - Service provider name and context
  - Best available time slots from family calendar
- Show draft to user for review before any sending
- Send via: SMS (Twilio), Zalo API (if connected), or copy-to-clipboard for manual sending
- **Always requires explicit user confirmation before any outbound message**
- Log all sent messages with timestamp

### 6. Family Calendar Integration
- Maintain local calendar (SQLite): recurring bills, one-time events, maintenance reminders
- Optional sync: read-only Google Calendar import for family availability
- Show: today's reminders, upcoming week's bills and maintenance
- Household members can all view (shared on local network)

### 7. Expense Tracking (Lightweight)
- Record paid bills → build monthly expense report
- Categories: điện (electricity), nước (water), internet, nhà/trọ (rent), xe (vehicle), bảo dưỡng (maintenance), other
- Simple charts: monthly totals by category
- Year-over-year comparison: "Điện tháng này tăng 15% so với cùng kỳ năm ngoái"

### 8. Self-Learning Knowledge Update
- Weekly crawl: EVN/SAWACO/VNPT/Viettel — check for new billing formats or contact info changes
- Update SECOND-KNOWLEDGE-BRAIN.md with: new utility bill formats, new payment methods, new common service categories
- Scrape (with permission): neighborhood Facebook groups or local service directories for trusted providers
- Knowledge base grows over time, improving bill parsing accuracy

---

## 📁 Project File Map

```
local-digital-concierge-agent/
├── CLAUDE.md                               ← You are here
├── PROJECT-detail.md                       ← Full technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md   ← Sprint tracker
├── SECOND-KNOWLEDGE-BRAIN.md               ← Living knowledge base
│
├── src/
│   ├── agents/
│   │   ├── orchestrator.py                 ← Main agent loop (runs locally)
│   │   ├── bill-processor/                 ← Vision API + document extraction
│   │   ├── scheduler/                      ← APScheduler-based reminder engine
│   │   ├── service-finder/                 ← OSM + Places API search
│   │   ├── message-drafter/                ← LLM message composition
│   │   ├── maintenance-tracker/            ← Vehicle & home maintenance logic
│   │   ├── expense-tracker/                ← Bill payment tracking + reports
│   │   └── knowledge-updater/              ← Utility info crawler
│   │
│   ├── database/
│   │   ├── schema.sql                      ← SQLite schema
│   │   ├── migrations/                     ← DB migration files
│   │   └── db_client.py                    ← SQLite connection pool
│   │
│   ├── prompts/
│   │   ├── bill-extraction-prompt.md       ← Vision API: extract bill data
│   │   ├── issue-classifier-prompt.md      ← Classify household issue type
│   │   ├── message-draft-prompt.md         ← Draft service request message
│   │   └── summary-prompt.md               ← Generate monthly summaries
│   │
│   ├── integrations/
│   │   ├── osm_client.py                   ← OpenStreetMap Overpass API
│   │   ├── google_places.py                ← Google Places API (optional)
│   │   ├── twilio_sender.py                ← SMS sending
│   │   ├── zalo_client.py                  ← Zalo messaging (optional)
│   │   └── calendar_sync.py               ← Google Calendar read-only sync
│   │
│   ├── tools/
│   │   ├── image_preprocessor.py           ← Bill photo enhancement
│   │   ├── llm_client.py                   ← Anthropic API wrapper (privacy-safe)
│   │   └── notification_manager.py         ← Push + audio notifications
│   │
│   └── ui/
│       ├── mobile-app/                     ← React Native (primary interface)
│       └── web-dashboard/                  ← Local web UI (home network access)
│
├── data/
│   ├── concierge.db                        ← SQLite database (ALL family data here)
│   └── backups/                            ← Automated local backups
│
├── tests/
│   ├── fixtures/
│   │   ├── bill-images/                    ← Sample Vietnamese bill photos
│   │   └── expected-extractions/           ← Ground truth for bill parsing
│   └── unit/ integration/
│
├── requirements.txt
├── .env.example                            ← API keys (all optional)
└── README.md
```

---

## 🔧 Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Runtime | Python 3.11+ | Best for local automation, scheduling, SQLite |
| Vision/LLM | Claude claude-sonnet-4-20250514 Vision + Text API | Best Vietnamese text extraction from bill photos |
| Local Database | SQLite (via `aiosqlite`) | Zero-dependency, local-only, perfect for household scale |
| Scheduler | APScheduler + asyncio | Local job scheduler, no cloud needed |
| Map/Places | OpenStreetMap Overpass API (free, no key) | Privacy-preserving, open data |
| Map/Places (enhanced) | Google Places API (optional) | Better ratings/reviews data if user provides key |
| SMS | Twilio (optional) | For actual SMS sending of service requests |
| Push Notifications | Firebase Cloud Messaging or local Ntfy | Cross-platform notifications |
| Mobile UI | React Native (Expo) | Single codebase iOS/Android |
| Web UI | FastAPI + React (local network only) | Dashboard on home WiFi |
| OCR Supplement | `easyocr` (Vietnamese + English) | Backup when Vision API unavailable |
| Expense Charts | `matplotlib` / Chart.js | Simple local charts, no cloud service |

---

## 🤖 ML/DL Strategy — Minimal AI, Maximum Privacy

### Philosophy
The AI API (Claude) is used **only when nothing simpler works**. Traditional algorithms handle scheduling, search, and storage. AI handles what rules can't: interpreting varied bill image formats and drafting natural language messages.

### Where AI Is Used (and Why It's the Right Tool)
| Task | Why AI (Not Rules) | Data Sent to API |
|------|-------------------|-----------------|
| Bill photo extraction | Vietnamese bills have 50+ formats across dozens of issuers; rules can't cover all | Only the bill image (no personal data pre-selected) |
| Issue classification | "Vòi nước bị hỏng" vs "Ống nước rò rỉ" vs "Bồn rửa tắc" require semantic understanding | Only the user's brief description (no address, no personal details) |
| Message drafting | Polite Vietnamese message context requires natural language understanding | Provider name + issue type + time slots (no personal data) |
| Monthly summary | Natural language summary of expense data | Only aggregated numbers (no bill details, no account numbers) |

### Where Traditional Algorithms Are Used (No AI)
| Task | Tool |
|------|------|
| Bill payment scheduling | APScheduler with cron expressions |
| Nearby service search | OpenStreetMap Overpass API + Haversine distance |
| Duplicate bill detection | SQLite UNIQUE constraints + fuzzy date matching |
| Expense categorization | Keyword rules + issuer lookup table |
| Calendar management | SQLite with recurring event logic |
| Maintenance interval calculation | Simple date/mileage arithmetic |

### Privacy-Safe API Call Pattern
```python
# CORRECT: Sanitize before sending to API
def extract_bill_data(bill_image: bytes) -> BillData:
    # Send: only the image bytes
    # Do NOT send: family name, address, account history
    raw_extraction = claude_vision.extract(bill_image, BILL_EXTRACTION_PROMPT)
    # Validate extracted data against known bill formats
    return validate_and_normalize(raw_extraction)

# CORRECT: Minimal context for message drafting
def draft_service_message(issue: str, provider_name: str, time_slots: list[str]) -> str:
    # Send: issue description, provider name, time slots
    # Do NOT send: home address, family name, previous bills, account numbers
    context = {"issue": issue, "provider": provider_name, "times": time_slots}
    return claude_text.draft(MESSAGE_DRAFT_PROMPT, context)
```

### HuggingFace Models (Local, Optional)
- `vinai/phobert-base-v2` — local issue classification (replaces API call when offline)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — semantic search over local service provider notes
- Used when: user chooses fully-offline mode or API is unavailable

---

## 📋 Prompt Engineering Guidelines

### Bill Extraction Prompt (Vision)
```
Extract structured data from this Vietnamese utility/household bill image.

Find and return ONLY the following fields (return null if not found):
- bill_type: "electricity" | "water" | "internet" | "phone" | "rent" | "loan" | "gas" | "other"
- issuer: Name of the company/organization issuing the bill
- account_number: Customer account or meter number (if visible)
- amount_due: Total amount to pay (numbers only, VND)
- due_date: Payment deadline (ISO format YYYY-MM-DD)
- billing_period_from: Start of billing period (YYYY-MM-DD or null)
- billing_period_to: End of billing period (YYYY-MM-DD or null)
- payment_methods: List of payment methods shown (e.g., ["bank transfer", "cash"])

Return as JSON only. Do not include any other text.
If this is not a bill, return {"error": "not_a_bill"}.
```

### Issue Classifier Prompt
```
The user described a household problem: "{user_description}"

Classify into ONE service category:
- "plumbing": water pipes, faucets, toilets, drains
- "electrical": power, switches, outlets, appliances
- "hvac": air conditioning, heating, ventilation
- "appliance": refrigerator, washing machine, oven, other appliances
- "structural": walls, roof, doors, windows, floors
- "pest_control": insects, rodents
- "cleaning": general cleaning services
- "other": anything else

Return JSON: {"category": "...", "urgency": "emergency|normal|low", "keywords": ["..."]}
Emergency = safety risk (gas leak, flood, fire, no power); Normal = daily disruption; Low = aesthetic/minor.
```

### Message Draft Prompt
```
Write a polite Vietnamese SMS/Zalo message to book a service appointment.

Context:
- Service needed: {issue_description}
- Provider name: {provider_name}  
- Preferred times: {time_slots}

Rules:
- Vietnamese only, warm and polite tone
- Under 160 characters if possible (SMS length)
- Include: what service is needed, preferred time options
- Do NOT include: home address (will be given if they reply), full name unless required
- End with a question: "Quý vị có thể sắp xếp không ạ?"

Draft only the message text, nothing else.
```

---

## ⚙️ Agent Behavioral Rules

1. **Always confirm before sending** — never send any message without explicit user approval ("Gửi đi nhé" or tap Send button).
2. **Local data, local storage** — all family data written to SQLite only; no cloud sync of personal data without explicit opt-in.
3. **Minimal API exposure** — strip personal identifiers before any API call; only issue type, provider info, and time slots go to LLM.
4. **Never auto-pay** — the agent can remind and draft, but never initiates financial transactions automatically.
5. **One action at a time** — for non-technical users, present one decision at a time; no overwhelming multi-step flows.
6. **Explain before doing** — always show what will happen before doing it: "Tôi sẽ tìm thợ sửa nước gần nhà mình và gợi ý 3 nơi tốt nhất. Được không?"
7. **Graceful degradation** — if Vision API is unavailable, prompt user to type bill details manually; if OSM search fails, show cached providers and suggest Google Maps search.
8. **User's trusted list wins** — always prioritize providers the user has marked as trusted over unknown OSM results.
9. **Update knowledge** — when new bill format or service category encountered, flag for knowledge base update.
10. **Privacy over convenience** — if a feature requires sharing data the user hasn't explicitly approved, don't use it.

---

## 🔒 Privacy & Security Model

### Data Classification
- **Family data** (never leaves device): bills, amounts, account numbers, addresses, vehicle info, family names, contact list
- **Anonymized fragments** (sent to Claude API only): bill images (contain account numbers — this is an accepted tradeoff), issue descriptions (stripped of names/addresses), provider names (public info)
- **Public data** (openly used): OpenStreetMap data, public business listings, utility company contact info

### Local Database Encryption
- SQLite file encrypted at rest using `sqlcipher` (optional, user-configurable)
- Encryption key stored in device keychain (not in the codebase)
- Automatic backup to local USB or NAS (never cloud by default)

### API Key Management
- All API keys in `.env` file (never committed)
- Anthropic key: required for bill extraction and message drafting
- Google Places, Twilio, Zalo: all optional — system degrades gracefully without them

---

## 🚀 Quick Start (for Claude Code)

```bash
# 1. Install
git clone <repo> && cd local-digital-concierge-agent
pip install -r requirements.txt

# 2. Initialize database
python src/database/init_db.py

# 3. Configure (minimal required: ANTHROPIC_API_KEY)
cp .env.example .env

# 4. Run agent
python src/agents/orchestrator.py

# 5. Mobile app (dev)
cd src/ui/mobile-app && npx expo start

# 6. Web dashboard (home network)
cd src/ui/web-dashboard && python -m uvicorn main:app --host 0.0.0.0 --port 8080

# 7. Test bill extraction
python -m pytest tests/ -v --sample-bill=tests/fixtures/bill-images/evn_sample.jpg

# 8. Update knowledge base
python src/agents/knowledge-updater/updater.py
```

---

## 📌 Key Conventions

- All monetary amounts stored as INTEGER (VND cents or full VND — consistent, documented)
- Dates stored as ISO 8601 strings in SQLite (`TEXT` type, not `DATE`)
- All Vietnamese text stored as UTF-8 NFC normalized
- Service providers stored with: name, phone, category, address, lat/lng, trust_level (user-trusted=2, good-rating=1, unknown=0)
- Bill status: `pending` → `reminded` → `paid` → `overdue` (state machine)
- Every outbound message stored in `messages_log` table before sending
- Backups run daily at 02:00 local time to `data/backups/` (rolling 7-day retention)
