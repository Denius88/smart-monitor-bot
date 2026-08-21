# Smart Monitor Bot

Telegram bot for automated product price monitoring and price-drop alerts.

Users can save product URLs, set a target price, choose an individual checking interval, view price history, and receive a Telegram notification when the target price is reached.

Built as a practical automation project demonstrating Python, Telegram bots, web scraping, asynchronous programming, SQLAlchemy, APScheduler, and Docker.

## Features

* Telegram bot interface with `/start`, `/add`, `/list`, `/history`, `/delete`, and `/cancel` commands.
* Button-based navigation for common actions.
* Guided multi-step flow for adding tracked products.
* URL, target-price, interval, and item-ID validation.
* Product price scraping with `curl_cffi` and BeautifulSoup.
* Store-specific price extraction for Rozetka, Epicentr, Amazon, eBay, and Books to Scrape.
* SQLite persistence through SQLAlchemy and `aiosqlite`.
* Separate monitoring intervals for each product.
* Persistent price history.
* `/history` command for viewing recent price changes.
* Scheduled background checks with APScheduler.
* Price-drop alerts with a direct product link.
* User-isolated tracked products.
* Environment-based configuration with `.env`.
* Docker and Docker Compose support.

## How It Works

1. The user starts the bot and selects **Add Item**.
2. The bot requests a product URL, target price, and checking interval in minutes.
3. The scraper attempts to retrieve the current product price.
4. The product and monitoring settings are stored in SQLite.
5. APScheduler runs a background job every minute.
6. Each tracked product is checked only when its individual interval has elapsed.
7. The current price is stored in the price history.
8. If the price reaches or falls below the target price, the bot sends a Telegram notification.

For example, a product configured with a `60` minute interval will be checked when at least one hour has passed since its previous check.

## Project Structure

```text
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

* Python 3.10+
* aiogram — Telegram Bot API framework
* SQLAlchemy — database ORM
* aiosqlite — asynchronous SQLite driver
* APScheduler — background scheduled jobs
* BeautifulSoup — HTML parsing
* curl_cffi — HTTP requests with browser-like TLS fingerprints
* SQLite — local persistence
* Docker / Docker Compose — containerized deployment

## Requirements

* Python 3.10 or newer
* Telegram bot token from BotFather
* Internet connection for Telegram API and product-page requests

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Denius88/smart-monitor-bot.git
cd smart-monitor-bot
```

### 2. Create a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

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

Create a `.env` file in the project root.

Use `.env.example` as a template:

```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///./monitor.db
LOG_LEVEL=INFO
```

Never commit the real Telegram bot token.

The repository ignores `.env`, SQLite databases, Python cache files, and other local development files.

### 5. Start the bot

```bash
python main.py
```

On the first startup, the application creates the SQLite database and starts the background scheduler.

Keep the process running while price monitoring is required.

## Bot Usage

### Add a Product

Use **Add Item** or `/add`.

The bot will ask for:

1. Supported product URL
2. Target price
3. Checking interval in minutes

### View Tracked Products

Use **My Items** or `/list`.

The bot displays:

* Item ID
* Product URL
* Current price
* Target price
* Monitoring interval

### View Price History

Use **Price History** or `/history`.

The bot displays the latest recorded prices for tracked products.

### Delete a Product

Use **Delete Item** or `/delete`.

Enter the item ID displayed by `/list`.

Users can delete only their own tracked products.

### Cancel an Action

Use **Cancel** or `/cancel` during a multi-step interaction.

## Supported Price Extraction

The scraper currently supports a small set of stores using store-specific CSS selectors:

* Rozetka
* Epicentr
* Amazon
* eBay
* Books to Scrape

A page may still be reachable while returning no price.

Possible reasons include:

* Changed page markup
* Product unavailable
* Store-side anti-bot protection
* Changed CSS selectors
* Temporary network problems

In this case, the tracked item remains saved and a future scheduled check can try again.

### Adding Another Store

To add support for another store, extend the price extraction logic in:

`smart_monitor/services/scraper.py`

Add the store domain and the appropriate price selector.

## Price History

Successful price observations are stored in the `PriceHistory` table.

This allows the bot to retain previous prices instead of storing only the latest value.

The history can be accessed through `/history`.

The current implementation displays the latest five recorded prices for each tracked item.

## Data Model

### User

Stores Telegram user information.

### TrackedItem

Stores:

* Owner
* Product URL
* Current price
* Target price
* Checking interval
* Last-check timestamp

### PriceHistory

Stores successful price observations associated with a tracked product.

The default database is a local SQLite file:

`monitor.db`

For a production deployment, SQLite could be replaced with PostgreSQL together with migrations, backups, and proper infrastructure.

## Scheduler

APScheduler runs the monitoring process in the background.

The scheduler wakes up once per minute and determines which products are due for another check.

Each product has its own monitoring interval.

This allows different products to be monitored at different frequencies without creating a separate scheduler job for every item.

## Validation and Error Handling

The bot validates:

* Product URLs
* Supported domains
* Target prices
* Checking intervals
* Product IDs
* User ownership

### `BOT_TOKEN is missing`

Check that `.env` exists in the project root and contains:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

### `ModuleNotFoundError`

Make sure the virtual environment is active and dependencies are installed:

```bash
python -m pip install -r requirements.txt
```

### No price found

Check that the URL belongs to a supported store.

The store's HTML structure or price selector may have changed.

### No alert appears

The scheduler runs every minute, but an individual product is checked only after its configured interval has elapsed.

## Docker

The project can also be run using Docker Compose.

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

Compile the application modules:

```bash
python -m py_compile main.py smart_monitor/main.py smart_monitor/models.py smart_monitor/config.py smart_monitor/database.py smart_monitor/bot/*.py smart_monitor/services/*.py
```

Check that the application imports successfully:

```bash
python -c "import main; print('Application import: OK')"
```

## What This Project Demonstrates

This project demonstrates a complete small-scale automation workflow:

* Asynchronous Telegram bot development
* Finite-state conversational input
* Web scraping
* Store-specific parsing
* Asynchronous database operations
* SQLAlchemy ORM
* Background scheduled jobs
* Persistent price history
* Input validation
* User-level data ownership
* Environment-based configuration
* Docker-based deployment

## Possible Production Improvements

For a production client deployment, the system could be extended with:

* PostgreSQL
* Database migrations
* Retry and rate-limit handling
* Structured logging
* Automated tests
* Monitoring and health checks
* Admin interface
* More store integrations
* Proxy rotation where appropriate
* Deployment with process supervision
* Metrics and alerting

## License

MIT License. See `LICENSE` for details.
