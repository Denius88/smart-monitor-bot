import asyncio
from scraper import check_price

async def test():
    test_url = "https://epicentrk.ua/ua/shop/blok-keramicheskiy-fp-klinker-2-nf-2-12.html"
    
    print(f"🔍 Йдемо на сайт: {test_url}")
    print("⏳ Чекаємо відповідь від сервера...\n")
    
    price = await check_price(test_url)
    
    if price:
        print(f"✅ Успіх! Парсер знайшов ціну: {price} грн.")
    else:
        print("❌ Не вдалося знайти ціну.")

if __name__ == "__main__":
    asyncio.run(test())