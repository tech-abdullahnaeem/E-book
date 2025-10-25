"""
Research Engine Module
Handles web research and information gathering
"""

import time
from typing import List, Dict, Optional
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup


class ResearchEngine:
    """Research engine for gathering information from web sources"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        """Initialize the research engine"""
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        
        if api_key and search_engine_id:
            try:
                self.search_service = build("customsearch", "v1", developerKey=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Google Search: {e}")
                self.search_service = None
        else:
            self.search_service = None
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for information using Google Custom Search"""
        
        if not self.search_service:
            return self._fallback_research(query)
        
        try:
            results = []
            response = self.search_service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=max_results
            ).execute()
            
            if 'items' in response:
                for item in response['items']:
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'Google Search'
                    })
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return self._fallback_research(query)
    
    def _fallback_research(self, query: str) -> List[Dict]:
        """Fallback research method when API is not available"""
        
        # Simple Wikipedia-based research
        try:
            import wikipedia
            
            search_results = wikipedia.search(query, results=3)
            results = []
            
            for title in search_results[:2]:
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                    results.append({
                        'title': page.title,
                        'link': page.url,
                        'snippet': wikipedia.summary(title, sentences=2),
                        'source': 'Wikipedia'
                    })
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Fallback research error: {e}")
            return []
    
    def get_scholarly_articles(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search for scholarly articles (placeholder for future implementation)"""
        
        # This would integrate with scholarly APIs like:
        # - Google Scholar API
        # - PubMed API
        # - arXiv API
        # - Semantic Scholar API
        
        return []
    
    def extract_facts(self, url: str) -> Dict:
        """Extract key facts from a URL"""
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main text content
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs[:5]])
            
            return {
                'url': url,
                'text': text[:500],  # First 500 characters
                'extracted': True
            }
            
        except Exception as e:
            return {
                'url': url,
                'text': '',
                'extracted': False,
                'error': str(e)
            }
