import os
import time
from urllib.parse import urlparse
from typing import List
from duckduckgo_search import DDGS
from langchain_core.tools import tool
from ..models.schemas import SearchResult

class WebSearcher:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")

    def _get_domain(self, url: str) -> str:
        try:
            domain = urlparse(url).netloc
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return "unknown"

    def _filter_results(self, raw_results: List[dict], max_results: int) -> List[SearchResult]:
        filtered = []
        domain_counts = {}
        
        exclude_domains = ["reddit.com", "quora.com", "pinterest.com", "youtube.com", "facebook.com", "twitter.com"]

        for res in raw_results:
            url = res.get("link", res.get("href", ""))
            domain = self._get_domain(url)
            
            if any(ex in domain for ex in exclude_domains):
                continue
                
            if domain_counts.get(domain, 0) >= 2:
                continue

            filtered.append(SearchResult(
                url=url,
                title=res.get("title", "No Title"),
                snippet=res.get("snippet", res.get("body", "")),
                source_domain=domain,
                fetched_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            ))
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            if len(filtered) >= max_results:
                break
                
        return filtered

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        print(f"[Search Engine] Searching for: '{query}'")
        if self.serpapi_key:
            return self._search_serpapi(query, num_results)
        else:
            return self._search_ddg(query, num_results)

    def _search_ddg(self, query: str, num_results: int) -> List[SearchResult]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results*2))
                return self._filter_results(results, num_results)
        except Exception as e:
            print(f"[Search Engine] DDG Error: {e}")
            return []

    def _search_serpapi(self, query: str, num_results: int) -> List[SearchResult]:
        try:
            from serpapi import GoogleSearch
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results * 2
            })
            results = search.get_dict().get("organic_results", [])
            return self._filter_results(results, num_results)
        except Exception as e:
            print(f"[Search Engine] SerpApi Error: {e}")
            return self._search_ddg(query, num_results) # Fallback

# Wrapper tool for Langchain
@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Searches the web for the given query and returns a list of URLs and snippets."""
    searcher = WebSearcher()
    results = searcher.search(query, max_results)
    
    output = []
    for r in results:
        output.append(f"Title: {r.title}\nURL: {r.url}\nSnippet: {r.snippet}\n")
    return "\n---\n".join(output)
