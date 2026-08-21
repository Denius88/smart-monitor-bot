from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
import re
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_html(url: str) -> Optional[str]:
    try:
        async with AsyncSession(impersonate="chrome120") as session:
            response = await session.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Failed to fetch {url}. Status: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def extract_price(html: str, domain: str) -> Optional[float]:
    soup = BeautifulSoup(html, "html.parser")
    
    try:
        price_text = None
        
        if "rozetka.com.ua" in domain:
            price_element = soup.select_one("p.product-price__big")
            if price_element:
                price_text = price_element.text
                
        elif "epicentrk.ua" in domain:
            price_element = soup.select_one('data[data-testid="product-main-price"]')
            if price_element:
                price_text = price_element.get("content") or price_element.text
                
        elif "amazon" in domain:
            price_element = soup.select_one("span.a-price span.a-offscreen, span.a-offscreen")
            if price_element:
                price_text = price_element.text
                
        elif "ebay" in domain:
            price_element = soup.select_one(".x-price-primary, .s-item__price")
            if price_element:
                price_text = price_element.text

        elif "books.toscrape.com" in domain:
            price_element = soup.select_one("p.price_color")
            if price_element:
                price_text = price_element.text
                
        if not price_text:
            return None
            
        price_text = price_text.replace("\xa0", "").replace(" ", "")
        last_comma = price_text.rfind(",")
        last_dot = price_text.rfind(".")

        if last_comma != -1 and last_dot != -1:
            if last_comma > last_dot:
                price_text = price_text.replace(".", "").replace(",", ".")
            else:
                price_text = price_text.replace(",", "")
        elif last_comma != -1:
            fractional_digits = len(price_text) - last_comma - 1
            price_text = price_text.replace(",", "." if fractional_digits in (1, 2) else "")

        clean_text = re.sub(r'[^\d.]', '', price_text)
        
        return float(clean_text)
        
    except Exception as e:
        logger.error(f"Error parsing HTML for domain {domain}: {e}")
        
    return None

async def check_price(url: str) -> Optional[float]:
    html = await fetch_html(url)
    if not html:
        return None
    
    domain = url.split("//")[-1].split("/")[0]
    return extract_price(html, domain)