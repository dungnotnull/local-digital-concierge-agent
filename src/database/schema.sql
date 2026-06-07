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
    notes TEXT,                        -- User notes: "S·∫°ch s·∫Ω, ƒë?∫ng gi·ªù, gi?° h·ª£p l?Ω"
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
    item_name TEXT NOT NULL,           -- "Xe m?°y Honda Wave - Thay nh·ªõt", "ƒêi·ªÅu h?≤a - V·ªá sinh l·ªçc"
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
    name TEXT,                         -- "Nh?† Nguy·ªÖn VƒÉn T?°m"
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
    extraction_hints TEXT,             -- JSON: hints for field extraction
    last_updated TEXT,                 -- When this format was last updated
    PRIMARY KEY (issuer, bill_type)
);
