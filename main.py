import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "Main Functionality"))
sys.path.insert(0, str(project_root / "Bot Functionality"))

from config import BOT_TOKEN
from database import init_db
import handlers
import scheduler 

async def main():
    logging.basicConfig(level=logging.INFO)
    
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(handlers.router)

    sched = scheduler.setup_scheduler(bot)
    sched.start()
    print("⏳ The task planner is up and running!")

    
    print("🚀 Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")