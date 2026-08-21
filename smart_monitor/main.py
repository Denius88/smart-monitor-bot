import asyncio
import logging

from aiogram import Bot, Dispatcher

from .bot import handlers
from .config import BOT_TOKEN, LOG_LEVEL
from .database import init_db
from .services import scheduler

async def main():
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))

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