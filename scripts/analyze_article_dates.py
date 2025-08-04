#!/usr/bin/env python3
"""
Article Date Analysis Tool - Analyze publication dates of detected changes
This tool helps determine if "new" articles are actually recent or old content.
"""

import asyncio
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
from bs4 import BeautifulSoup

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


class ArticleDateAnalyzer:
    """Analyze publication dates of articles."""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def extract_article_date(self, url: str) -> Dict[str, Any]:
        """Extract publication date from an article page."""
        try:
            async with self.session.get(url, timeout=15) as response:
                if response.status != 200:
                    return {
                        'url': url,
                        'status': response.status,
                        'date_found': False,
                        'date': None,
                        'date_source': 'error'
                    }
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Try multiple date extraction methods
                date_info = await self._extract_date_from_page(soup, url)
                
                return {
                    'url': url,
                    'status': 200,
                    'date_found': date_info['found'],
                    'date': date_info['date'],
                    'date_source': date_info['source']
                }
                
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'date_found': False,
                'date': None,
                'date_source': f'error: {str(e)}'
            }
    
    async def _extract_date_from_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract date from page using multiple methods."""
        
        # Method 1: Look for meta tags
        meta_date = self._extract_meta_date(soup)
        if meta_date:
            return {'found': True, 'date': meta_date, 'source': 'meta_tag'}
        
        # Method 2: Look for structured data
        structured_date = self._extract_structured_date(soup)
        if structured_date:
            return {'found': True, 'date': structured_date, 'source': 'structured_data'}
        
        # Method 3: Look for common date patterns in text
        text_date = self._extract_text_date(soup)
        if text_date:
            return {'found': True, 'date': text_date, 'source': 'text_content'}
        
        # Method 4: Extract from URL patterns (for Judiciary UK)
        url_date = self._extract_url_date(url)
        if url_date:
            return {'found': True, 'date': url_date, 'source': 'url_pattern'}
        
        return {'found': False, 'date': None, 'source': 'not_found'}
    
    def _extract_meta_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract date from meta tags."""
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="article:published_time"]',
            'meta[property="og:updated_time"]',
            'meta[name="date"]',
            'meta[name="pubdate"]',
            'meta[name="publishdate"]',
            'meta[name="dc.date"]',
            'meta[name="dc.date.issued"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                return meta['content']
        
        return None
    
    def _extract_structured_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract date from structured data (JSON-LD)."""
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Look for datePublished or dateCreated
                    date = data.get('datePublished') or data.get('dateCreated') or data.get('dateModified')
                    if date:
                        return date
                    
                    # Check if it's an Article type
                    if data.get('@type') == 'Article':
                        date = data.get('datePublished') or data.get('dateCreated')
                        if date:
                            return date
            except:
                continue
        
        return None
    
    def _extract_text_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract date from text content using regex patterns."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        
        # Common date patterns
        date_patterns = [
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}-\d{1,2}-\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_url_date(self, url: str) -> Optional[str]:
        """Extract date from URL patterns (specific to Judiciary UK)."""
        # Look for date patterns in URL
        date_patterns = [
            r'/(\d{4})/(\d{2})/(\d{2})/',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})_(\d{2})_(\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, url)
            if match:
                if len(match.groups()) == 3:
                    year, month, day = match.groups()
                    return f"{year}-{month}-{day}"
        
        return None
    
    async def analyze_changes_file(self, changes_file: str, max_articles: int = 10) -> Dict[str, Any]:
        """Analyze publication dates of articles in a changes file."""
        print(f"📊 Analyzing article dates in: {changes_file}")
        
        with open(changes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract new pages
        changes = data.get('changes', {}).get('methods', {}).get('hybrid', {}).get('changes', [])
        new_urls = [c['url'] for c in changes if c['change_type'] == 'new']
        
        print(f"📈 Found {len(new_urls)} new articles")
        
        # Analyze first N articles to avoid overwhelming the server
        analyze_urls = new_urls[:max_articles]
        print(f"🔍 Analyzing first {len(analyze_urls)} articles...")
        
        results = []
        recent_articles = []
        old_articles = []
        no_date_articles = []
        
        for url in analyze_urls:
            result = await self.extract_article_date(url)
            results.append(result)
            
            if result['date_found'] and result['date']:
                try:
                    # Parse the date
                    date_str = result['date']
                    if 'T' in date_str:
                        date_str = date_str.split('T')[0]
                    
                    article_date = datetime.strptime(date_str, '%Y-%m-%d')
                    current_date = datetime.now()
                    
                    # Consider articles from last 3 months as "recent"
                    three_months_ago = current_date.replace(month=current_date.month - 3)
                    
                    if article_date >= three_months_ago:
                        recent_articles.append({
                            'url': url,
                            'date': article_date.strftime('%Y-%m-%d'),
                            'source': result['date_source']
                        })
                    else:
                        old_articles.append({
                            'url': url,
                            'date': article_date.strftime('%Y-%m-%d'),
                            'source': result['date_source']
                        })
                except:
                    no_date_articles.append({
                        'url': url,
                        'date': result['date'],
                        'source': result['date_source']
                    })
            else:
                no_date_articles.append({
                    'url': url,
                    'date': None,
                    'source': result['date_source']
                })
        
        # Print results
        print(f"\n📊 Date Analysis Results:")
        print(f"   Recent articles (last 3 months): {len(recent_articles)}")
        print(f"   Old articles (>3 months): {len(old_articles)}")
        print(f"   No date found: {len(no_date_articles)}")
        
        if recent_articles:
            print(f"\n✅ Recent articles:")
            for article in recent_articles:
                print(f"   📅 {article['date']} - {article['url']}")
        
        if old_articles:
            print(f"\n⚠️  Old articles (false positives?):")
            for article in old_articles:
                print(f"   📅 {article['date']} - {article['url']}")
        
        if no_date_articles:
            print(f"\n❓ Articles with no date found:")
            for article in no_date_articles:
                print(f"   ❓ {article['url']} (source: {article['source']})")
        
        return {
            'recent_articles': recent_articles,
            'old_articles': old_articles,
            'no_date_articles': no_date_articles,
            'total_analyzed': len(analyze_urls)
        }


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_article_dates.py <changes_file> [max_articles]")
        print("Example: python analyze_article_dates.py output/20250804_140143/Judiciary\\ UK_20250804_140210.json 15")
        return 1
    
    changes_file = sys.argv[1]
    max_articles = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    if not os.path.exists(changes_file):
        print(f"❌ Changes file not found: {changes_file}")
        return 1
    
    print("🚀 Starting article date analysis...")
    
    async with ArticleDateAnalyzer() as analyzer:
        results = await analyzer.analyze_changes_file(changes_file, max_articles)
    
    print(f"\n📊 Analysis complete!")
    print(f"💡 Insights:")
    print(f"   - Recent articles are likely genuine new content")
    print(f"   - Old articles might be sitemap updates of existing content")
    print(f"   - This helps identify if changes are real or just sitemap maintenance")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 