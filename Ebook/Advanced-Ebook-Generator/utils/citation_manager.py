"""
Citation Manager Module
Handles citations and bibliography generation
"""

from typing import List, Dict
from datetime import datetime


class CitationManager:
    """Manages citations and bibliography"""
    
    def __init__(self, style: str = "APA"):
        """Initialize citation manager"""
        self.style = style
        self.citations = []
    
    def add_citation(self, citation_data: Dict):
        """Add a citation"""
        self.citations.append(citation_data)
    
    def format_citation(self, citation_data: Dict) -> str:
        """Format a single citation based on style"""
        
        if self.style == "APA":
            return self._format_apa(citation_data)
        elif self.style == "MLA":
            return self._format_mla(citation_data)
        elif self.style == "Chicago":
            return self._format_chicago(citation_data)
        elif self.style == "Harvard":
            return self._format_harvard(citation_data)
        else:
            return self._format_apa(citation_data)
    
    def _format_apa(self, data: Dict) -> str:
        """Format citation in APA style"""
        
        authors = data.get('authors', ['Unknown Author'])
        year = data.get('year', datetime.now().year)
        title = data.get('title', 'Untitled')
        source = data.get('source', 'Web')
        url = data.get('url', '')
        
        author_str = self._format_authors_apa(authors)
        
        if url:
            return f"{author_str} ({year}). *{title}*. {source}. Retrieved from {url}"
        else:
            return f"{author_str} ({year}). *{title}*. {source}."
    
    def _format_mla(self, data: Dict) -> str:
        """Format citation in MLA style"""
        
        authors = data.get('authors', ['Unknown Author'])
        title = data.get('title', 'Untitled')
        source = data.get('source', 'Web')
        year = data.get('year', datetime.now().year)
        url = data.get('url', '')
        
        author_str = self._format_authors_mla(authors)
        
        if url:
            return f"{author_str}. \"{title}.\" *{source}*, {year}, {url}."
        else:
            return f"{author_str}. \"{title}.\" *{source}*, {year}."
    
    def _format_chicago(self, data: Dict) -> str:
        """Format citation in Chicago style"""
        
        authors = data.get('authors', ['Unknown Author'])
        year = data.get('year', datetime.now().year)
        title = data.get('title', 'Untitled')
        source = data.get('source', 'Web')
        url = data.get('url', '')
        
        author_str = self._format_authors_chicago(authors)
        
        if url:
            return f"{author_str}. {year}. \"{title}.\" *{source}*. {url}."
        else:
            return f"{author_str}. {year}. \"{title}.\" *{source}*."
    
    def _format_harvard(self, data: Dict) -> str:
        """Format citation in Harvard style"""
        
        authors = data.get('authors', ['Unknown Author'])
        year = data.get('year', datetime.now().year)
        title = data.get('title', 'Untitled')
        source = data.get('source', 'Web')
        url = data.get('url', '')
        
        author_str = self._format_authors_harvard(authors)
        
        if url:
            return f"{author_str} ({year}) '{title}', *{source}*. Available at: {url}."
        else:
            return f"{author_str} ({year}) '{title}', *{source}*."
    
    def _format_authors_apa(self, authors: List[str]) -> str:
        """Format authors for APA"""
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    def _format_authors_mla(self, authors: List[str]) -> str:
        """Format authors for MLA"""
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]}, et al"
    
    def _format_authors_chicago(self, authors: List[str]) -> str:
        """Format authors for Chicago"""
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    def _format_authors_harvard(self, authors: List[str]) -> str:
        """Format authors for Harvard"""
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    def generate_bibliography(self) -> str:
        """Generate complete bibliography"""
        
        if not self.citations:
            return """## Bibliography

*This e-book was generated using AI technology and incorporates general knowledge and established research. 
Specific citations are available upon request.*
"""
        
        bib_text = f"## Bibliography\n\n*Citations formatted in {self.style} style*\n\n"
        
        for citation in sorted(self.citations, key=lambda x: x.get('authors', [''])[0]):
            bib_text += f"- {self.format_citation(citation)}\n\n"
        
        return bib_text
    
    def add_web_source(self, title: str, url: str, authors: List[str] = None, year: int = None):
        """Add a web source citation"""
        
        self.add_citation({
            'title': title,
            'url': url,
            'authors': authors or ['Web Source'],
            'year': year or datetime.now().year,
            'source': 'Online'
        })
