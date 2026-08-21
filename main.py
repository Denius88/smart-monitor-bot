import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db
from handlers import router

async def main():
    logging.basicConfig(level=logging.INFO)
    
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    print("🚀 Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")