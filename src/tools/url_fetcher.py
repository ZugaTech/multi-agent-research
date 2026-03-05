import asyncio
import httpx
import time
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List, Optional

class FetchedPage(BaseModel):
    url: str
    title: str
    text: str
    word_count: int
    fetch_time_ms: float

class URLFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def fetch_single(self, url: str) -> Optional[FetchedPage]:
        start_time = time.time()
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get("content-type", "").lower()
                if not "text/html" in content_type and not "text/plain" in content_type:
                    return None

                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                
                title = soup.title.string if soup.title else "No Title"
                title = title.strip()
                
                # Remove unwanted elements
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()
                
                # Extract text
                text = soup.get_text(separator="\n")
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                clean_text = "\n".join(lines)
                
                words = clean_text.split()
                if len(words) > 3000:
                    clean_text = " ".join(words[:3000]) # Truncate to save tokens
                    
                word_count = len(clean_text.split())
                fetch_time = (time.time() - start_time) * 1000
                
                if word_count < 50: # Skip pages with almost no content
                    return None
                    
                return FetchedPage(
                    url=url,
                    title=title,
                    text=clean_text,
                    word_count=word_count,
                    fetch_time_ms=fetch_time
                )
        except Exception as e:
            print(f"[URLFetcher] Failed to fetch {url}: {e}")
            return None

    async def fetch_batch(self, urls: List[str]) -> List[FetchedPage]:
        tasks = [self.fetch_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_pages = []
        for r in results:
            if isinstance(r, FetchedPage):
                valid_pages.append(r)
        return valid_pages
