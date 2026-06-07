# Local Digital Concierge Agent

A privacy-first, local-first household management agent that runs entirely on your device. Built for Vietnamese households but adaptable globally.

## Overview

The Local Digital Concierge Agent is a comprehensive household management system that handles:

- Bill & Document Ingestion: Extract data from bill photos using AI vision
- Smart Reminder Scheduler: Payment and maintenance reminders with escalation
- Vehicle & Home Maintenance Tracker: Service interval tracking
- Local Service Finder: Find trusted providers via OpenStreetMap
- Message Drafting & Sending: Polite Vietnamese service requests
- Family Calendar Integration: Shared reminders and events
- Expense Tracking: Monthly reports and year-over-year comparisons
- Self-Learning Knowledge System: Updates bill formats and provider info

All data stays on your device in an encrypted SQLite database. AI is used only for bill extraction and message drafting, with privacy-preserving practices.

## Quick Start

```bash
# Clone repository
git clone https://github.com/dungnotnull/local-digital-concierge-agent
cd local-digital-concierge-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment (required: ANTHROPIC_API_KEY)
cp .env.example .env
# Edit .env to add your API keys

# Initialize database
python src/database/init_db.py

# Run the agent
python src/agents/orchestrator.py

# For development:
# Mobile app: cd src/ui/mobile-app && npx expo start
# Web dashboard: cd src/ui/web-dashboard && uvicorn main:app --reload
```

## Architecture

### Local-First Design
- Primary data store: SQLite database (`data/concierge.db`) on your device
- AI usage: Minimal and privacy-safe - only bill images and brief text snippets sent to Claude API
- Optional cloud services: Google Places, Twilio, Zalo (graceful degradation without them)

### Core Components
```
src/
??? agents/
?   ??? bill-processor/
?   ?   ??? bill_processor.py
?   ?   ??? image_preprocessor.py
?   ?   ??? __init__.py
?   ??? scheduler/
?   ?   ??? scheduler.py
?   ?   ??? __init__.py
?   ??? service-finder/
?   ?   ??? service_finder.py
?   ?   ??? __init__.py
?   ??? message-drafter/
?   ?   ??? message_drafter.py
?   ?   ??? __init__.py
?   ??? maintenance-tracker/
?   ?   ??? maintenance_tracker.py
?   ?   ??? __init__.py
?   ??? expense-tracker/
?   ?   ??? expense_tracker.py
?   ?   ??? __init__.py
?   ??? knowledge-updater/
?   ?   ??? knowledge_updater.py
?   ?   ??? __init__.py
?   ??? orchestrator.py
??? database/
?   ??? db_client.py
?   ??? migration.py
?   ??? schema.sql
?   ??? __init__.py
??? integrations/
?   ??? __init__.py
??? models/
?   ??? __init__.py
??? prompts/
?   ??? bill-extraction-prompt.md
?   ??? issue-classifier-prompt.md
?   ??? message-draft-prompt.md
?   ??? summary-prompt.md
?   ??? __init__.py
??? tools/
?   ??? backup.py
?   ??? llm_client.py
?   ??? __init__.py
??? ui/
    ??? __init__.py
    ??? web-dashboard/
        ??? main.py
        ??? __init__.py
```

## Privacy & Security

- Data never leaves device except:
  - Bill images sent to Claude Vision for extraction (contains account numbers - accepted tradeoff)
  - Brief text snippets for message drafting (issue type, provider name, time slots)
- Local encryption: Optional SQLCipher for database-at-rest encryption
- API keys stored locally in `.env` (never committed)
- Audit trails: All actions logged locally
- Backups: Automatic daily local backups with 7-day retention

## Supported Platforms

- Android phone (primary target - reuse old device)
- Raspberry Pi 4 (always-on home server)
- Windows/macOS laptop (development/testing)
- Web dashboard accessible on home network
- React Native mobile app (in development)

## Development

### Prerequisites
- Python 3.11+
- Node.js 18+ (for mobile/web frontend)
- Git

### Setup
```bash
# Backend
pip install -r requirements.txt

# Frontend (web dashboard)
cd src/ui/web-dashboard
pip install -r requirements.txt  # if any frontend deps added

# Mobile app (React Native)
cd src/ui/mobile-app
npm install
```

### Testing
```bash
# Run unit tests
pytest tests/unit/

# Run all tests
pytest tests/
```

### Code Quality
```bash
# Linting
ruff check .

# Type checking
mypy src/
```

## Documentation

- CLAUDE.md - Agent identity, capabilities, and technical specification
- PROJECT-detail.md - Full technical specification
- SECOND-KNOWLEDGE-BRAIN.md - Living knowledge base
- PROJECT-DEVELOPMENT-PHASE-TRACKING.md - Development progress

## License

MIT License - see [LICENSE] file.

## Acknowledgments

- Built with Claude AI by Anthropic
- Inspired by local-first software principles
- Vietnamese household management practices

---

*Your family's quiet digital manager - bills tracked, maintenance scheduled, repairmen found. All running on your own device.
