from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
import re
import logging
from typing import Optional

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_html(url: str) -> Optional[str]:
    """Fetch HTML bypassing Cloudflare using curl_cffi."""
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
    """Parse HTML and extract the price based on website-specific logic."""
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
            
        if ',' in price_text and '.' in price_text:
            price_text = price_text.replace(',', '')
        elif ',' in price_text and '.' not in price_text:
            price_text = price_text.replace(',', '.')
            
        clean_text = re.sub(r'[^\d.]', '', price_text)
        
        return float(clean_text)
        
    except Exception as e:
        logger.error(f"Error parsing HTML for domain {domain}: {e}")
        
    return None

async def check_price(url: str) -> Optional[float]:
    """Main entry point to get the current price from a URL."""
    html = await fetch_html(url)
    if not html:
        return None
    
    domain = url.split("//")[-1].split("/")[0]
    return extract_price(html, domain)