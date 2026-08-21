import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select
from aiogram import Bot

from ..database import AsyncSessionLocal
from ..models import PriceHistory, TrackedItem
from .scraper import check_price

logger = logging.getLogger(__name__)

async def check_all_prices(bot: Bot):
    now = datetime.now(timezone.utc)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(TrackedItem))
        items = result.scalars().all()
        
        for item in items:
            last_checked = item.last_checked
            if last_checked.tzinfo is None:
                last_checked = last_checked.replace(tzinfo=timezone.utc)
                
            time_since_last = now - last_checked
            if time_since_last.total_seconds() < (item.check_interval * 60):
                continue 
                
            logger.info(f"🔍 Checking: {item.url}")
            current_price = await check_price(item.url)
            
            item.last_checked = now
            
            if current_price is None:
                continue

            session.add(PriceHistory(tracked_item_id=item.id, price=current_price, checked_at=now))
                
            if item.current_price != current_price:
                item.current_price = current_price
                
                if current_price <= item.target_price:
                    msg = (
                        "🎉 <b>PRICE DROP ALERT!</b> 🎉\n\n"
                        f"🔥 <b>The price just dropped to:</b> <code>{current_price}</code>\n"
                        f"🎯 <i>Your target was:</i> {item.target_price}\n\n"
                        f"🛒 <a href='{item.url}'>Click here to view/buy it!</a>\n\n"
                        "<i>I will keep tracking it according to your schedule.</i>"
                    )
                    try:
                        await bot.send_message(chat_id=item.user_id, text=msg, parse_mode="HTML")
                    except Exception as e:
                        logger.error(f"Could not send msg to {item.user_id}: {e}")
                        
        await session.commit()

def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    
    scheduler.add_job(check_all_prices, 'interval', minutes=1, args=[bot])
    
    return scheduler