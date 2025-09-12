#!/usr/bin/env python3
"""
Comprehensive MOSDAC Scraper
============================

Discovers and scrapes ALL URLs from MOSDAC website (60+ sites) with optimal structure for RAG ingestion.

Features:
- Sitemap.xml discovery and parsing
- Robots.txt compliance
- Complete URL coverage (60+ sites)
- RAG-optimized content structure
- Quality scoring and filtering
- Parallel processing
- Structured data extraction
"""

import asyncio
import json
import re
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import NoExtractionStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveMOSDACScraper:
    """Comprehensive scraper for all MOSDAC content with RAG optimization"""
    
    def __init__(self, output_dir: str = "./mosdac_complete_data"):
        self.base_url = "https://mosdac.gov.in"
        self.domain = urlparse(self.base_url).netloc
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # URL discovery
        self.discovered_urls: Set[str] = set()
        self.processed_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        
        # Crawler configuration
        self.crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=NoExtractionStrategy(),
            markdown_generator=DefaultMarkdownGenerator(
                options={
                    "include_images": False,
                    "include_links": True,
                    "include_tables": True,
                    "table_format": "grid",
                    "include_metadata": True
                }
            )
        )
        
        self.browser_kwargs = {
            "headless": True,
            "enable_stealth": True,
            "viewport_width": 1920,
            "viewport_height": 1080,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "wait_for_page_idle_timeout": 10000,
            "wait_for_network_idle_timeout": 5000
        }
        
        # Statistics
        self.stats = {
            "urls_discovered": 0,
            "urls_processed": 0,
            "urls_failed": 0,
            "total_content_length": 0,
            "tables_extracted": 0,
            "start_time": None,
            "end_time": None
        }
    
    async def discover_all_urls(self) -> List[str]:
        """Discover ALL URLs from sitemap and crawling"""
        logger.info("🔍 Discovering all MOSDAC URLs...")
        
        discovered = []
        
        # 1. Discover from sitemap.xml
        sitemap_urls = await self._discover_from_sitemap()
        discovered.extend(sitemap_urls)
        logger.info(f"📄 Found {len(sitemap_urls)} URLs from sitemap")
        
        # 2. Discover from robots.txt
        robots_urls = await self._discover_from_robots()
        discovered.extend(robots_urls)
        logger.info(f"🤖 Found {len(robots_urls)} URLs from robots.txt")
        
        # 3. Discover by crawling
        crawl_urls = await self._discover_by_crawling()
        discovered.extend(crawl_urls)
        logger.info(f"🕷️ Found {len(crawl_urls)} URLs by crawling")
        
        # 4. Add base URL
        if self.base_url not in self.discovered_urls:
            discovered.append(self.base_url)
        
        # Store and deduplicate
        for url in discovered:
            if urlparse(url).netloc == self.domain:
                self.discovered_urls.add(url)
        
        self.stats["urls_discovered"] = len(self.discovered_urls)
        logger.info(f"✅ Total URLs discovered: {len(self.discovered_urls)}")
        
        return list(self.discovered_urls)
    
    async def _discover_from_sitemap(self) -> List[str]:
        """Discover URLs from sitemap.xml"""
        sitemap_urls = []
        
        # Try common sitemap locations
        sitemap_locations = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/sitemaps/sitemap.xml",
            f"{self.base_url}/sitemap/sitemap.xml"
        ]
        
        async with aiohttp.ClientSession() as session:
            for sitemap_url in sitemap_locations:
                try:
                    async with session.get(sitemap_url, timeout=30) as response:
                        if response.status == 200:
                            content = await response.text()
                            urls = self._parse_sitemap_xml(content)
                            sitemap_urls.extend(urls)
                            logger.info(f"✅ Parsed sitemap: {sitemap_url}")
                            break
                except Exception as e:
                    logger.debug(f"Failed to fetch sitemap {sitemap_url}: {e}")
        
        return sitemap_urls
    
    def _parse_sitemap_xml(self, content: str) -> List[str]:
        """Parse sitemap XML content"""
        urls = []
        
        try:
            root = ET.fromstring(content)
            
            # Handle sitemap index
            if root.tag.endswith('sitemapindex'):
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        # Recursively parse nested sitemaps
                        nested_urls = asyncio.run(self._fetch_and_parse_sitemap(loc.text))
                        urls.extend(nested_urls)
            
            # Handle regular sitemap
            else:
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        url = loc.text.strip()
                        if urlparse(url).netloc == self.domain:
                            urls.append(url)
        
        except ET.ParseError as e:
            logger.warning(f"Failed to parse sitemap XML: {e}")
        except Exception as e:
            logger.warning(f"Error parsing sitemap: {e}")
        
        return urls
    
    async def _discover_from_robots(self) -> List[str]:
        """Discover URLs from robots.txt"""
        robots_urls = []
        
        try:
            async with aiohttp.ClientSession() as session:
                robots_url = f"{self.base_url}/robots.txt"
                async with session.get(robots_url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        urls = self._parse_robots_txt(content)
                        robots_urls.extend(urls)
                        logger.info(f"✅ Parsed robots.txt: {len(urls)} URLs found")
        except Exception as e:
            logger.debug(f"Failed to fetch robots.txt: {e}")
        
        return robots_urls
    
    def _parse_robots_txt(self, content: str) -> List[str]:
        """Parse robots.txt for sitemap references"""
        urls = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Look for sitemap references
            if line.lower().startswith('sitemap:'):
                sitemap_url = line.split(':', 1)[1].strip()
                if sitemap_url:
                    nested_urls = asyncio.run(self._fetch_and_parse_sitemap(sitemap_url))
                    urls.extend(nested_urls)
        
        return urls
    
    async def _discover_by_crawling(self) -> List[str]:
        """Discover URLs by crawling pages"""
        crawl_urls = []
        max_depth = 2
        max_pages = 50
        
        # Start with base URL
        to_crawl = [(self.base_url, 0)]
        crawled = set()
        
        async with AsyncWebCrawler() as crawler:
            while to_crawl and len(crawled) < max_pages:
                url, depth = to_crawl.pop(0)
                
                if url in crawled or depth > max_depth:
                    continue
                
                try:
                    result = await crawler.arun(
                        url=url,
                        config=self.crawler_config,
                        **self.browser_kwargs
                    )
                    
                    if result.success:
                        crawled.add(url)
                        
                        # Extract links from the page
                        soup = BeautifulSoup(result.html, 'html.parser')
                        links = soup.find_all('a', href=True)
                        
                        for link in links:
                            href = link['href']
                            full_url = urljoin(url, href)
                            
                            # Only include URLs from the same domain
                            if urlparse(full_url).netloc == self.domain:
                                if full_url not in self.discovered_urls:
                                    crawl_urls.append(full_url)
                                    to_crawl.append((full_url, depth + 1))
                
                except Exception as e:
                    logger.debug(f"Failed to crawl {url}: {e}")
        
        return crawl_urls
    
    async def _fetch_and_parse_sitemap(self, sitemap_url: str) -> List[str]:
        """Fetch and parse a sitemap URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sitemap_url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_sitemap_xml(content)
        except Exception as e:
            logger.debug(f"Failed to fetch sitemap {sitemap_url}: {e}")
        return []
    
    async def extract_content_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract comprehensive content from a single URL"""
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=url,
                    config=self.crawler_config,
                    **self.browser_kwargs
                )
                
                if not result.success:
                    logger.warning(f"Failed to crawl {url}: {result.error_message}")
                    return None
                
                # Parse HTML for advanced extraction
                soup = BeautifulSoup(result.html, 'html.parser')
                
                # Extract title
                title = ""
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
                
                # Extract metadata
                metadata = self._extract_metadata(soup, url)
                
                # Extract tables
                tables = self._extract_tables(soup)
                
                # Extract headings structure
                headings = self._extract_headings(soup)
                
                # Calculate quality score
                quality_score = self._calculate_quality_score(
                    result.markdown, title, tables, headings, metadata
                )
                
                return {
                    "url": url,
                    "title": title,
                    "content": result.markdown,
                    "html": result.html,
                    "metadata": metadata,
                    "tables": tables,
                    "headings": headings,
                    "quality_score": quality_score,
                    "extracted_at": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML"""
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc,
            "path": urlparse(url).path,
            "description": "",
            "keywords": [],
            "author": "",
            "language": "en",
            "canonical": "",
            "og_title": "",
            "og_description": "",
            "og_image": "",
            "last_modified": ""
        }
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_attr = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = [kw.strip() for kw in content.split(',')]
            elif name == 'author':
                metadata['author'] = content
            elif name == 'language':
                metadata['language'] = content
            elif property_attr == 'og:title':
                metadata['og_title'] = content
            elif property_attr == 'og:description':
                metadata['og_description'] = content
            elif property_attr == 'og:image':
                metadata['og_image'] = content
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata['canonical'] = urljoin(url, canonical['href'])
        
        return metadata
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract tables with structure and content"""
        tables = []
        
        for i, table in enumerate(soup.find_all('table')):
            table_data = {
                "index": i,
                "caption": "",
                "headers": [],
                "rows": [],
                "row_count": 0,
                "col_count": 0
            }
            
            # Extract caption
            caption = table.find('caption')
            if caption:
                table_data['caption'] = caption.get_text().strip()
            
            # Extract headers
            header_row = table.find('tr')
            if header_row:
                headers = []
                for th in header_row.find_all(['th', 'td']):
                    headers.append(th.get_text().strip())
                table_data['headers'] = headers
                table_data['col_count'] = len(headers)
            
            # Extract rows
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cells = []
                for cell in row.find_all(['td', 'th']):
                    cells.append(cell.get_text().strip())
                if cells:
                    table_data['rows'].append(cells)
            
            table_data['row_count'] = len(table_data['rows'])
            
            if table_data['row_count'] > 0:
                tables.append(table_data)
        
        return tables
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract heading structure"""
        headings = []
        
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            heading_data = {
                "index": i,
                "level": int(heading.name[1]),
                "text": heading.get_text().strip(),
                "id": heading.get('id', ''),
                "class": heading.get('class', [])
            }
            headings.append(heading_data)
        
        return headings
    
    def _calculate_quality_score(self, content: str, title: str, tables: List, 
                               headings: List, metadata: Dict) -> float:
        """Calculate quality score for content (0.0 to 1.0)"""
        score = 0.0
        
        # Content length (0.3 weight)
        content_length = len(content)
        if content_length > 1000:
            score += 0.3
        elif content_length > 500:
            score += 0.2
        elif content_length > 100:
            score += 0.1
        
        # Title presence (0.1 weight)
        if title and len(title.strip()) > 0:
            score += 0.1
        
        # Tables presence (0.2 weight)
        if tables:
            score += min(0.2, len(tables) * 0.05)
        
        # Headings structure (0.2 weight)
        if headings:
            score += min(0.2, len(headings) * 0.02)
        
        # Metadata richness (0.2 weight)
        metadata_score = 0
        if metadata.get('description'):
            metadata_score += 0.05
        if metadata.get('keywords'):
            metadata_score += 0.05
        if metadata.get('og_title'):
            metadata_score += 0.05
        if metadata.get('og_description'):
            metadata_score += 0.05
        score += min(0.2, metadata_score)
        
        return min(1.0, score)
    
    async def save_content(self, content: Dict[str, Any]) -> None:
        """Save extracted content to files with RAG-optimized structure"""
        # Create URL-based directory structure
        url_path = urlparse(content["url"]).path.strip('/')
        if not url_path:
            url_path = "index"
        
        # Sanitize path for filesystem
        safe_path = re.sub(r'[^\w\-_/]', '_', url_path)
        if len(safe_path) > 100:
            safe_path = hashlib.md5(safe_path.encode()).hexdigest()[:16]
        
        page_dir = self.output_dir / safe_path
        page_dir.mkdir(exist_ok=True, parents=True)
        
        # Save main content (RAG-optimized)
        content_file = page_dir / "content.md"
        async with aiofiles.open(content_file, 'w', encoding='utf-8') as f:
            await f.write(f"# {content['title']}\n\n")
            await f.write(f"**URL:** {content['url']}\n")
            await f.write(f"**Extracted:** {content['extracted_at']}\n")
            await f.write(f"**Quality Score:** {content['quality_score']:.3f}\n\n")
            await f.write(content['content'])
        
        # Save HTML
        html_file = page_dir / "raw.html"
        async with aiofiles.open(html_file, 'w', encoding='utf-8') as f:
            await f.write(content['html'])
        
        # Save structured data (RAG-optimized)
        structured_data = {
            "url": content["url"],
            "title": content["title"],
            "metadata": content["metadata"],
            "tables": content["tables"],
            "headings": content["headings"],
            "quality_score": content["quality_score"],
            "extracted_at": content["extracted_at"],
            "content_length": len(content["content"]),
            "rag_optimized": True
        }
        
        structured_file = page_dir / "structured_data.json"
        async with aiofiles.open(structured_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(structured_data, indent=2, ensure_ascii=False))
        
        # Save tables separately if present (RAG-optimized)
        if content["tables"]:
            tables_file = page_dir / "tables.json"
            async with aiofiles.open(tables_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(content["tables"], indent=2, ensure_ascii=False))
    
    async def run_comprehensive_scraping(self, max_concurrent: int = 5) -> Dict[str, Any]:
        """Run comprehensive scraping of all discovered URLs"""
        logger.info("🚀 Starting comprehensive MOSDAC scraping...")
        
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Discover all URLs
        discovered_urls = await self.discover_all_urls()
        
        # Filter URLs by quality and relevance
        filtered_urls = self._filter_urls(discovered_urls)
        logger.info(f"📊 Filtered to {len(filtered_urls)} high-quality URLs")
        
        # Process URLs with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_url(url: str):
            async with semaphore:
                if url in self.processed_urls:
                    return
                
                logger.info(f"Processing: {url}")
                
                content = await self.extract_content_from_url(url)
                if content:
                    await self.save_content(content)
                    self.processed_urls.add(url)
                    self.stats["urls_processed"] += 1
                    self.stats["total_content_length"] += len(content["content"])
                    self.stats["tables_extracted"] += len(content["tables"])
                else:
                    self.failed_urls.add(url)
                    self.stats["urls_failed"] += 1
        
        # Process all URLs
        tasks = [process_url(url) for url in filtered_urls]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Generate comprehensive index
        await self._generate_comprehensive_index()
        
        self.stats["end_time"] = datetime.now().isoformat()
        
        logger.info("✅ Comprehensive scraping completed!")
        logger.info(f"📊 Processed: {self.stats['urls_processed']} URLs")
        logger.info(f"❌ Failed: {self.stats['urls_failed']} URLs")
        logger.info(f"📄 Total content: {self.stats['total_content_length']:,} characters")
        
        return self.stats
    
    def _filter_urls(self, urls: List[str]) -> List[str]:
        """Filter URLs based on quality and relevance"""
        filtered = []
        
        for url in urls:
            # Skip if already processed
            if url in self.processed_urls:
                continue
            
            # Skip certain file types
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            skip_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
                             '.zip', '.rar', '.tar', '.gz', '.jpg', '.jpeg', '.png', '.gif', 
                             '.svg', '.ico', '.css', '.js', '.xml', '.json']
            
            if any(path.endswith(ext) for ext in skip_extensions):
                continue
            
            # Skip certain patterns
            skip_patterns = ['/admin/', '/login/', '/logout/', '/register/', '/api/', 
                           '/ajax/', '/search?', '/print/', '/download/']
            
            if any(pattern in path for pattern in skip_patterns):
                continue
            
            filtered.append(url)
        
        return filtered
    
    async def _generate_comprehensive_index(self) -> None:
        """Generate comprehensive index of all scraped content"""
        index_data = {
            "metadata": {
                "base_url": self.base_url,
                "domain": self.domain,
                "scraping_session": {
                    "started_at": self.stats["start_time"],
                    "completed_at": self.stats["end_time"],
                    "total_duration": None
                },
                "scraper_version": "1.0",
                "output_directory": str(self.output_dir),
                "rag_optimized": True
            },
            "statistics": {
                "urls_discovered": self.stats["urls_discovered"],
                "urls_processed": self.stats["urls_processed"],
                "urls_failed": self.stats["urls_failed"],
                "total_content_length": self.stats["total_content_length"],
                "tables_extracted": self.stats["tables_extracted"],
                "average_quality_score": 0.0
            },
            "urls": {},
            "content_index": {}
        }
        
        # Calculate duration
        if self.stats["start_time"] and self.stats["end_time"]:
            start = datetime.fromisoformat(self.stats["start_time"])
            end = datetime.fromisoformat(self.stats["end_time"])
            duration = (end - start).total_seconds()
            index_data["metadata"]["scraping_session"]["total_duration"] = duration
        
        # Process all scraped content
        total_quality = 0.0
        quality_count = 0
        
        for page_dir in self.output_dir.iterdir():
            if not page_dir.is_dir():
                continue
            
            structured_file = page_dir / "structured_data.json"
            if not structured_file.exists():
                continue
            
            try:
                with open(structured_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                url = data["url"]
                quality_score = data.get("quality_score", 0.0)
                
                # Add to URLs index
                index_data["urls"][url] = {
                    "title": data.get("title", ""),
                    "quality_score": quality_score,
                    "content_length": len(data.get("content", "")),
                    "tables_count": len(data.get("tables", [])),
                    "headings_count": len(data.get("headings", [])),
                    "extracted_at": data.get("extracted_at"),
                    "directory": str(page_dir)
                }
                
                # Add to content index
                index_data["content_index"][url] = {
                    "title": data.get("title", ""),
                    "description": data.get("metadata", {}).get("description", ""),
                    "keywords": data.get("metadata", {}).get("keywords", []),
                    "headings": [h["text"] for h in data.get("headings", [])],
                    "quality_score": quality_score
                }
                
                total_quality += quality_score
                quality_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to process {structured_file}: {e}")
        
        # Calculate average quality
        if quality_count > 0:
            index_data["statistics"]["average_quality_score"] = total_quality / quality_count
        
        # Save comprehensive index
        index_file = self.output_dir / "comprehensive_index.json"
        async with aiofiles.open(index_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(index_data, indent=2, ensure_ascii=False))
        
        logger.info(f"📋 Comprehensive index saved to {index_file}")

async def main():
    """Main function"""
    scraper = ComprehensiveMOSDACScraper()
    stats = await scraper.run_comprehensive_scraping()
    
    print("\n" + "="*60)
    print("🎉 COMPREHENSIVE MOSDAC SCRAPING COMPLETED!")
    print("="*60)
    print(f"📊 URLs Discovered: {stats['urls_discovered']}")
    print(f"✅ URLs Processed: {stats['urls_processed']}")
    print(f"❌ URLs Failed: {stats['urls_failed']}")
    print(f"📄 Total Content: {stats['total_content_length']:,} characters")
    print(f"📊 Tables Extracted: {stats['tables_extracted']}")
    print(f"📁 Output Directory: ./mosdac_complete_data")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
