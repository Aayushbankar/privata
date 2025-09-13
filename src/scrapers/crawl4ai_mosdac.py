#!/usr/bin/env python3
"""
Enhanced MOSDAC crawler using Crawl4AI with structured data extraction.
This crawler replaces the old scraping approach with modern, intelligent crawling.
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import NoExtractionStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import html2text

class MOSDACCrawler:
    """Enhanced MOSDAC crawler using Crawl4AI with structured data extraction"""
    
    def __init__(self, output_dir: str = "./crawl4ai_output_enhanced"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        
        # MOSDAC website structure
        self.mosdac_base_url = "https://mosdac.gov.in"
        self.important_pages = [
            "/",  # Home page
            "/insat-3dr", "/insat-3d", "/kalpana-1", "/insat-3a",
            "/megha-tropiques", "/saral-altika", "/oceansat-2", 
            "/oceansat-3", "/insat-3ds", "/scatsat-1",
            "/about-us", "/contact-us", "/data-access-policy",
            "/privacy-policy", "/terms-conditions", "/faq-page",
            "/tools", "/sitemap", "/help"
        ]
        
        # Crawler configuration
        self.crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=NoExtractionStrategy(),
            markdown_generator=DefaultMarkdownGenerator(
                options={
                    "include_images": False,
                    "include_links": True,
                    "include_tables": True,
                    "table_format": "grid"
                }
            )
        )
        
        # Browser settings to pass as kwargs
        self.browser_kwargs = {
            "headless": True,
            "enable_stealth": True,
            "viewport_width": 1920,
            "viewport_height": 1080,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "wait_for_page_idle_timeout": 5000,
            "wait_for_network_idle_timeout": 3000
        }
    
    def extract_mission_info(self, content: str, url: str) -> Dict[str, Any]:
        """Extract structured mission information from content"""
        mission_patterns = {
            "mission_name": r"(INSAT-3D[R]?|KALPANA-1|MeghaTropiques|SARAL-AltiKa|OCEANSAT-[23]|SCATSAT-1|INSAT-3DS)",
            "launch_dates": r"Launch(?:ed)?\s*(?:on|date)?[:]?\s*(\d{1,2}\s+\w+\s+\d{4}|\d{4}-\d{2}-\d{2})",
            "satellite_type": r"(Meteorological|Communication|Earth Observation|Weather) Satellite",
            "instrumentation": r"Instruments?[:]?([^\.]+\.)",
            "orbit_type": r"(Geostationary|Polar|Sun-synchronous) orbit",
            "mission_status": r"(Operational|Retired|Active|Decommissioned)"
        }
        
        mission_info = {"url": url, "extracted_at": datetime.now().isoformat()}
        
        for key, pattern in mission_patterns.items():
            matches = []
            try:
                if key == "mission_name":
                    # Special handling for mission names - look for exact matches
                    mission_names = ["INSAT-3DR", "INSAT-3D", "KALPANA-1", "MeghaTropiques", 
                                   "SARAL-AltiKa", "OCEANSAT-2", "OCEANSAT-3", "INSAT-3DS", "SCATSAT-1"]
                    for name in mission_names:
                        if name.lower() in content.lower():
                            matches.append(name)
                else:
                    # Use regex for other patterns
                    import re
                    found = re.findall(pattern, content, re.IGNORECASE)
                    matches = [m.strip() for m in found if m.strip()]
                
                mission_info[key] = matches if matches else []
            except Exception as e:
                mission_info[key] = []
                print(f"Error extracting {key}: {e}")
        
        return mission_info
    
    def extract_technical_specs(self, content: str) -> Dict[str, List[str]]:
        """Extract technical specifications from content"""
        tech_patterns = {
            "orbit_parameters": r"(Altitude|Inclination|Period|Eccentricity)[:\s]+([\d\.]+)\s*(km|degrees|minutes)?",
            "sensor_types": r"(Imager|Sounder|Radiometer|Spectrometer|Camera|Scanner)",
            "frequency_bands": r"(\d+\.\d+\s*GHz|\d+\s*MHz)",
            "resolution": r"Resolution[:\s]+([\d\.]+\s*(km|m|meters?))",
            "coverage": r"Coverage[:\s]+([^\.]+\.?)",
            "data_products": r"(L1B|L2|L3|L4)[\s\-]*([\w\s]+)"
        }
        
        tech_specs = {}
        import re
        
        for key, pattern in tech_patterns.items():
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Flatten tuple matches and clean up
                    cleaned_matches = []
                    for match in matches:
                        if isinstance(match, tuple):
                            cleaned_matches.append(' '.join([m for m in match if m]).strip())
                        else:
                            cleaned_matches.append(match.strip())
                    tech_specs[key] = list(set(cleaned_matches))
                else:
                    tech_specs[key] = []
            except Exception as e:
                tech_specs[key] = []
                print(f"Error extracting {key}: {e}")
        
        return tech_specs

    def save_structured_data(self, url: str, markdown_content: str, html_content: str, 
                           mission_info: Dict[str, Any], tech_specs: Dict[str, List[str]]) -> None:
        """Save structured data in multiple formats"""
        from urllib.parse import urlparse
        import hashlib
        
        # Create filename from URL
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        if not path:
            path = "home"
        
        filename_base = path.replace('/', '_')
        if len(filename_base) > 100:
            filename_base = hashlib.md5(filename_base.encode()).hexdigest()[:16]
        
        # Create output directory for this page
        page_dir = self.output_dir / filename_base
        page_dir.mkdir(exist_ok=True)
        
        # Save markdown content
        markdown_path = page_dir / "content.md"
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(f"# {url}\n\n")
            f.write(f"Extracted: {datetime.now().isoformat()}\n\n")
            f.write(markdown_content)
        
        # Save HTML content (raw)
        html_path = page_dir / "raw.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save structured data as JSON
        structured_data = {
            "url": url,
            "extracted_at": datetime.now().isoformat(),
            "mission_info": mission_info,
            "technical_specs": tech_specs,
            "metadata": {
                "content_length": len(markdown_content),
                "html_length": len(html_content),
                "has_tables": "table" in markdown_content.lower()
            }
        }
        
        json_path = page_dir / "structured_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved data for {url} to {page_dir}")

    async def crawl_page(self, url: str) -> None:
        """Crawl a single page with enhanced processing"""
        try:
            async with AsyncWebCrawler() as crawler:
                print(f"Crawling: {url}")
                
                result = await crawler.arun(
                    url=url,
                    config=self.crawler_config,
                    **self.browser_kwargs
                )
                
                if result.success:
                    # Extract structured information
                    mission_info = self.extract_mission_info(result.markdown, url)
                    tech_specs = self.extract_technical_specs(result.markdown)
                    
                    # Save all data
                    self.save_structured_data(
                        url=url,
                        markdown_content=result.markdown,
                        html_content=result.html,
                        mission_info=mission_info,
                        tech_specs=tech_specs
                    )
                    
                    print(f"Successfully processed {url}")
                    print(f"Mission info: {mission_info.get('mission_name', [])}")
                    print(f"Technical specs found: {len(tech_specs)} categories")
                    
                else:
                    print(f"Failed to crawl {url}: {result.error_message}")
                    
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    async def crawl_all_pages(self) -> None:
        """Crawl all important MOSDAC pages"""
        tasks = []
        
        for page in self.important_pages:
            url = f"{self.mosdac_base_url}{page}"
            tasks.append(self.crawl_page(url))
        
        # Run with limited concurrency to avoid overwhelming the server
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
        
        async def limited_crawl(url):
            async with semaphore:
                return await self.crawl_page(url)
        
        # Run all tasks
        await asyncio.gather(*[limited_crawl(url) for url in 
                             [f"{self.mosdac_base_url}{page}" for page in self.important_pages]])
        
        print("Crawling completed!")
        
        # Generate summary report
        self.generate_summary_report()
        
    def generate_summary_report(self) -> None:
        """Generate a summary report of the crawling process"""
        import json
        from pathlib import Path
        
        summary = {
            "total_pages_crawled": len(self.important_pages),
            "crawled_at": datetime.now().isoformat(),
            "pages": []
        }
        
        for page_dir in self.output_dir.iterdir():
            if page_dir.is_dir():
                json_file = page_dir / "structured_data.json"
                if json_file.exists():
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        summary["pages"].append({
                            "url": data["url"],
                            "content_length": data["metadata"]["content_length"],
                            "html_length": data["metadata"]["html_length"],
                            "has_tables": data["metadata"]["has_tables"],
                            "mission_info_found": len(data["mission_info"]["mission_name"]) > 0,
                            "tech_specs_found": any(len(specs) > 0 for specs in data["technical_specs"].values())
                        })
        
        # Save summary report
        summary_path = self.output_dir / "crawling_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Summary report saved to {summary_path}")
        
        # Print quick stats
        successful_crawls = len([p for p in summary["pages"] if p["content_length"] > 0])
        print(f"\nCrawling Summary:")
        print(f"- Total pages attempted: {summary['total_pages_crawled']}")
        print(f"- Successfully crawled: {successful_crawls}")
        print(f"- Mission info extracted: {len([p for p in summary['pages'] if p['mission_info_found']])}")
        print(f"- Technical specs found: {len([p for p in summary['pages'] if p['tech_specs_found']])}")

    def clean_old_data(self) -> None:
        """Clean up old crawled data"""
        import shutil
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        print(f"Cleaned old data from {self.output_dir}")

async def main():
    """Main function to run the enhanced MOSDAC crawler"""
    crawler = MOSDACCrawler()
    
    print("Starting enhanced MOSDAC crawling with Crawl4AI...")
    print("=" * 60)
    
    # Clean old data
    crawler.clean_old_data()
    
    # Start crawling
    await crawler.crawl_all_pages()
    
    print("=" * 60)
    print("Crawling completed! Check the output directory for results.")

if __name__ == "__main__":
    asyncio.run(main())
