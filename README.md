# Smart Monitor Bot

Smart Monitor is a Telegram price-tracking bot built as a practical automation project. Users save product URLs, set a target price, choose an individual checking interval, and receive a Telegram alert when the price reaches their target.

The project is suitable as a portfolio example for freelance automation work, Telegram bots, web scraping, and lightweight data-driven services.

## Features

- Telegram bot interface with `/start`, `/add`, `/list`, `/delete`, and `/cancel` commands.
- Button-based navigation for the main user actions.
- Guided multi-step flow for adding a tracked product.
- URL, target-price, interval, and item-ID validation.
- Product price scraping with `curl_cffi` and BeautifulSoup.
- Store-specific selectors for Rozetka, Epicentr, Amazon, eBay, and Books to Scrape.
- SQLite persistence through SQLAlchemy and `aiosqlite`.
- Separate tracking intervals per product.
- Persistent price history with a `/history` command.
- Scheduled background checks through APScheduler.
- Price-drop alerts with a direct product link.
- User-isolated item lists and deletion.
- Local secrets through a `.env` file.

## How It Works

1. A user starts the bot and chooses **Add Item**.
2. The bot asks for a product URL, target price, and check interval in minutes.
3. The scraper attempts to read the current price.
4. The product and its monitoring settings are saved in `monitor.db`.
5. APScheduler wakes up every minute and checks only products whose individual interval has elapsed.
6. When a current price is at or below the target price, the bot sends an alert.

The scheduler runs once per minute, while each item controls its own effective frequency. For example, an item configured for 60 minutes is checked when its last check is at least one hour old.

## Project Structure

```text
Smart Monitor/
├── main.py                         # Local launcher
├── smart_monitor/                  # Application package
│   ├── main.py                     # Application entry point
│   ├── models.py                   # SQLAlchemy data models
│   ├── bot/handlers.py             # Telegram commands and FSM flows
│   └── services/                   # Scraper and scheduler
├── requirements.txt                # Runtime dependencies
├── .env                            # Local bot token, not committed
├── monitor.db                      # Local SQLite database, not committed
├── .env.example                    # Configuration template
├── Dockerfile                      # Container image definition
├── docker-compose.yml              # Local/host deployment definition
└── .dockerignore                   # Build context exclusions
```

## Requirements

- Python 3.10 or newer
- A Telegram bot token from [BotFather](https://t.me/BotFather)
- Internet access for Telegram API calls and product-page requests

## Installation

### 1. Clone or download the project

```bash
git clone <your-repository-url>
cd "Smart Monitor"
```

### 2. Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure the bot token

Create a file named `.env` in the project root:

```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///./monitor.db
LOG_LEVEL=INFO
```

Never commit the real token. The repository ignores `.env`, `monitor.db`, and Python cache folders.

### 5. Start the bot

```bash
python main.py
```

On first startup, the application creates the local SQLite database and starts the background scheduler. Keep the process running while you want price monitoring to continue.

## Bot Usage

### Add a product

Use **Add Item** or `/add`, then provide:

1. A supported product URL.
2. The target price, such as `500` or `1500.50`.
3. The check interval in minutes, such as `15`, `60`, or `1440`.

### View tracked products

Use **My Items** or `/list` to see item IDs, URLs, current prices, target prices, and monitoring intervals.

### View price history

Use **Price History** or `/history` to see the latest five recorded prices for each tracked item.

### Delete a product

Use **Delete Item** or `/delete`, then send the item ID shown by `/list`.

### Cancel an action

Use **Cancel** or `/cancel` during any multi-step flow.

## Supported Price Extraction

The scraper currently uses known CSS selectors for a small set of sites. A page can still be reachable while returning no price if its markup has changed, the product is unavailable, or the site blocks automated requests. In that case, the item remains saved and the next scheduled check can try again.

To add another store, extend `extract_price()` in `smart_monitor/services/scraper.py` with the store domain and its current price selector.

## Data Model

- `User` stores the Telegram user ID and username.
- `TrackedItem` stores the owner, URL, current price, target price, check interval, and last-check timestamp.
- `PriceHistory` stores successful price observations linked to a tracked item.
- The SQLite database is created locally as `monitor.db`.
- Database records are intentionally local for this sample project. A production deployment could use PostgreSQL, migrations, backups, and encrypted infrastructure.

## Validation and Troubleshooting

Compile all modules:

```bash
python -m py_compile main.py smart_monitor/main.py smart_monitor/models.py smart_monitor/config.py smart_monitor/database.py smart_monitor/bot/*.py smart_monitor/services/*.py
```

Check that imports resolve without starting polling:

```bash
python -c "import main; print('Application import: OK')"
```

Common issues:

- `BOT_TOKEN is missing`: verify that `.env` is in the project root and contains `BOT_TOKEN=...`.
- `ModuleNotFoundError`: activate the virtual environment and install `requirements.txt`.
- No price found: confirm that the URL belongs to a supported store and inspect the store's current HTML selectors.
- No alert appears: remember that the scheduler runs every minute and the product is checked only after its configured interval has elapsed.

## Docker

Create `.env` from `.env.example`, add your Telegram token, and run:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f smart-monitor
```

Stop the service:

```bash
docker compose down
```

## Portfolio Notes

This project demonstrates a complete small automation workflow:

- asynchronous Telegram interaction;
- finite-state conversational input;
- asynchronous persistence;
- scheduled background jobs;
- site-specific scraping;
- validation and user-level data ownership;
- environment-based configuration.

For a production client project, the next upgrades would typically include a hosted database, deployment with process supervision, structured logging, retry and rate-limit handling, monitoring, automated tests, and an admin interface.

## License

This project is provided as a portfolio and learning example. Add a license file before distributing it as a reusable product.
