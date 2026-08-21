# 🛒 Smart Monitor Bot: Automated Price Tracking Service

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/Telegram_Bot-aiogram-blue.svg?logo=telegram)](https://docs.aiogram.dev/)
[![SQLAlchemy](https://img.shields.io/badge/Database-SQLAlchemy-red.svg)](https://www.sqlalchemy.org/)
[![APScheduler](https://img.shields.io/badge/Scheduler-APScheduler-orange.svg)](https://apscheduler.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

Smart Monitor Bot is an asynchronous Python-based Telegram bot that tracks product prices across multiple e-commerce platforms and notifies users the moment a target price is reached. It combines web scraping, scheduled background checks, and persistent price history into a single automation service.

The project demonstrates production-style backend patterns: async I/O, per-user data isolation, individually scheduled jobs, and containerized deployment.

## ✨ Core Features

- **Multi-Store Support:** Extracts prices from Rozetka, Epicentr, Amazon, eBay, and Books to Scrape via store-specific selectors.
- **Guided Bot Flow:** Conversational, button-driven interface (`/add`, `/list`, `/history`, `/delete`) with full input validation (URL, price, interval, item ID).
- **Per-Item Scheduling:** Each tracked product has its own checking interval — a single APScheduler job efficiently manages all of them.
- **Price History:** Every successful check is stored, letting users review recent price movement with `/history`.
- **Resilient Scraping:** Uses `curl_cffi` for browser-like TLS fingerprinting plus BeautifulSoup parsing, with graceful handling of unavailable pages or changed markup.
- **User Isolation:** Every tracked item belongs to a single Telegram user; no cross-user data access.
- **Containerized Deployment:** Ready-to-run Docker and Docker Compose setup.

## 🛠️ Technical Stack

- **Bot Framework:** aiogram (async Telegram Bot API)
- **Database Layer:** SQLAlchemy ORM + `aiosqlite` (async SQLite)
- **Scheduling:** APScheduler (background interval-based jobs)
- **Scraping:** `curl_cffi`, BeautifulSoup
- **Deployment:** Docker, Docker Compose
- **Configuration:** Environment variables via `.env`

## 🏗️ Project Structure

```
smart-monitor-bot/
├── main.py
├── smart_monitor/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── bot/
│   │   └── handlers.py
│   └── services/
│       ├── scraper.py
│       └── scheduler.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- A Telegram bot token from [BotFather](https://t.me/BotFather)

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/Denius88/smart-monitor-bot.git
cd smart-monitor-bot
```

2. **Install dependencies:**

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. **Configure environment:** create `.env` from `.env.example`:

```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///./monitor.db
LOG_LEVEL=INFO
```

### Running the Bot

```bash
python main.py
```

On first launch, the SQLite database is created automatically and the background scheduler starts. Keep the process running for continuous monitoring.

### Running with Docker

```bash
docker compose up -d --build
docker compose logs -f smart-monitor   # view logs
docker compose down                    # stop
```

## 🤖 How It Works

1. User sends `/add` and provides a product URL, target price, and checking interval (minutes).
2. The scraper fetches the current price and the item is saved to SQLite.
3. APScheduler wakes up every minute and checks which items are due, based on their individual interval.
4. Each successful check is logged to price history.
5. Once the price hits the target, the user gets an instant Telegram alert with a direct product link.

## 🎯 Architecture Highlights for Developers

- **Per-item scheduling without job sprawl:** rather than spawning one APScheduler job per product, a single minute-tick job evaluates due items against their stored interval — keeping the scheduler lightweight regardless of how many products are tracked.
- **Graceful scraping failures:** a missing price (anti-bot walls, markup changes, temporary downtime) never deletes the tracked item — it simply waits for the next scheduled attempt.
- **Async all the way down:** aiogram, aiosqlite, and APScheduler's async executor keep the bot responsive under concurrent users.
- **Extensible store support:** adding a new store is a matter of registering a domain and CSS selector in `services/scraper.py` — no changes to the bot or scheduler logic required.

## ⚠️ Disclaimer

This project is built for educational and portfolio demonstration purposes. Users are responsible for complying with the terms of service of the tracked websites and applicable data-scraping regulations.

## License

MIT License. See `LICENSE` for details.
