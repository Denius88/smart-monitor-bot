# Smart Monitor Bot 🛒📉

A Telegram bot for automated product price monitoring and price-drop alerts.

Users save product URLs, set a target price, and choose a checking interval — the bot tracks the price on its own and sends a Telegram notification once the target price is reached.

Built as a practical automation project demonstrating Python, Telegram bots, web scraping, asynchronous programming, SQLAlchemy, APScheduler, and Docker.

---

## 📋 Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Bot Usage](#bot-usage)
- [Supported Stores](#supported-stores)
- [Data Model](#data-model)
- [Scheduler](#scheduler)
- [Troubleshooting](#troubleshooting)
- [Docker](#docker)
- [Possible Production Improvements](#possible-production-improvements)
- [License](#license)

---

## Features

- Telegram bot interface with `/start`, `/add`, `/list`, `/history`, `/delete`, and `/cancel` commands
- Button-based navigation for common actions
- Guided multi-step flow for adding tracked products
- URL, target-price, interval, and item-ID validation
- Product price scraping with `curl_cffi` and BeautifulSoup
- Store-specific price extraction for Rozetka, Epicentr, Amazon, eBay, and Books to Scrape
- SQLite persistence through SQLAlchemy and `aiosqlite`
- Separate monitoring interval for each product
- Persistent price history
- `/history` command for viewing recent price changes
- Scheduled background checks with APScheduler
- Price-drop alerts with a direct product link
- User-isolated tracked products
- Environment-based configuration with `.env`
- Docker and Docker Compose support

## How It Works

1. The user starts the bot and selects **Add Item**.
2. The bot requests a product URL, target price, and checking interval in minutes.
3. The scraper attempts to retrieve the current product price.
4. The product and monitoring settings are stored in SQLite.
5. APScheduler runs a background job every minute.
6. Each tracked product is checked only once its individual interval has elapsed.
7. The current price is stored in the price history.
8. If the price reaches or falls below the target price, the bot sends a Telegram notification.

> For example, a product configured with a `60`-minute interval will be checked once at least one hour has passed since its previous check.

## Project Structure

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
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Tech Stack

| Component | Purpose |
|---|---|
| Python 3.10+ | Development language |
| aiogram | Telegram Bot API framework |
| SQLAlchemy | Database ORM |
| aiosqlite | Asynchronous SQLite driver |
| APScheduler | Background scheduled jobs |
| BeautifulSoup | HTML parsing |
| curl_cffi | HTTP requests with browser-like TLS fingerprints |
| SQLite | Local persistence |
| Docker / Docker Compose | Containerized deployment |

## Requirements

- Python 3.10 or newer
- A Telegram bot token from BotFather
- Internet connection for Telegram API and product-page requests

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Denius88/smart-monitor-bot.git
cd smart-monitor-bot
```

### 2. Create a virtual environment

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root, using `.env.example` as a template:

```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///./monitor.db
LOG_LEVEL=INFO
```

⚠️ Never commit your real Telegram bot token. `.env`, SQLite databases, Python cache files, and other local development files are already ignored via `.gitignore`.

### 5. Start the bot

```bash
python main.py
```

On first startup, the application creates the SQLite database and starts the background scheduler. Keep the process running while price monitoring is required.

## Bot Usage

### Add a Product
`/add` or the **Add Item** button — the bot asks for a product URL, target price, and checking interval (in minutes).

### View Tracked Products
`/list` or the **My Items** button — displays item ID, product URL, current price, target price, and monitoring interval.

### View Price History
`/history` or the **Price History** button — shows the latest recorded prices for tracked products (currently the last 5 entries per item).

### Delete a Product
`/delete` or the **Delete Item** button — enter the item ID shown by `/list`. Users can delete only their own tracked products.

### Cancel an Action
`/cancel` or the **Cancel** button — cancels the current multi-step interaction.

## Supported Stores

The scraper uses store-specific CSS selectors for price extraction:

- Rozetka
- Epicentr
- Amazon
- eBay
- Books to Scrape

A page may still be reachable while returning no price. Possible reasons include changed page markup, an unavailable product, store-side anti-bot protection, changed CSS selectors, or temporary network problems. In this case, the tracked item remains saved and a future scheduled check can try again.

**Adding another store:** extend the price extraction logic in `smart_monitor/services/scraper.py` by adding the store domain and the appropriate price selector.

## Data Model

| Entity | Description |
|---|---|
| **User** | Telegram user information |
| **TrackedItem** | Owner, product URL, current price, target price, checking interval, last-check timestamp |
| **PriceHistory** | Successful price observations associated with a tracked product |

The default database is a local SQLite file, `monitor.db`. For a production deployment, SQLite could be replaced with PostgreSQL together with migrations, backups, and proper infrastructure.

## Scheduler

APScheduler runs the monitoring process in the background. It wakes up once per minute and determines which products are due for another check. Each product has its own monitoring interval, allowing different products to be monitored at different frequencies without creating a separate scheduler job for every item.

## Troubleshooting

**`BOT_TOKEN is missing`**
Check that `.env` exists in the project root and contains `BOT_TOKEN=your_telegram_bot_token_here`.

**`ModuleNotFoundError`**
Make sure the virtual environment is active and dependencies are installed:
```bash
python -m pip install -r requirements.txt
```

**No price found**
Check that the URL belongs to a supported store. The store's HTML structure or price selector may have changed.

**No alert appears**
The scheduler runs every minute, but an individual product is checked only after its configured interval has elapsed.

## Docker

### 1. Configure environment
Create `.env` from `.env.example` and add your Telegram bot token.

### 2. Build and start
```bash
docker compose up -d --build
```

### 3. View logs
```bash
docker compose logs -f smart-monitor
```

### 4. Stop the service
```bash
docker compose down
```

## Validation

```bash
python -m py_compile main.py smart_monitor/main.py smart_monitor/models.py smart_monitor/config.py smart_monitor/database.py smart_monitor/bot/*.py smart_monitor/services/*.py

python -c "import main; print('Application import: OK')"
```

## What This Project Demonstrates

- Asynchronous Telegram bot development
- Finite-state conversational input flows
- Web scraping and store-specific parsing
- Asynchronous database operations with SQLAlchemy ORM
- Background scheduled jobs
- Persistent price history
- Input validation and user-level data ownership
- Environment-based configuration
- Docker-based deployment

## Possible Production Improvements

- PostgreSQL
- Database migrations
- Retry and rate-limit handling
- Structured logging
- Automated tests
- Monitoring and health checks
- Admin interface
- More store integrations
- Proxy rotation where appropriate
- Deployment with process supervision (systemd, supervisord)
- Metrics and alerting

## License

MIT License. See `LICENSE` for details.
