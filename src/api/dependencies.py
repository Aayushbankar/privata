"""
Dependency injection module for MOSDAC AI Help Bot API.

This module provides dependency functions to avoid circular imports.
"""

from typing import Optional
from src.core.mosdac_bot import MOSDACBot
from src.scrapers.comprehensive_mosdac_scraper import ComprehensiveMOSDACScraper
from src.ingestion.ingest import ModernIngestionPipeline

# Global instances (singleton pattern)
bot_instance: Optional[MOSDACBot] = None
scraper_instance: Optional[ComprehensiveMOSDACScraper] = None
ingestor_instance: Optional[ModernIngestionPipeline] = None

def get_bot() -> MOSDACBot:
    """Get or create MOSDACBot instance."""
    global bot_instance
    if bot_instance is None:
        bot_instance = MOSDACBot()
    return bot_instance

def get_scraper() -> ComprehensiveMOSDACScraper:
    """Get or create scraper instance."""
    global scraper_instance
    if scraper_instance is None:
        scraper_instance = ComprehensiveMOSDACScraper()
    return scraper_instance

def get_ingestor() -> ModernIngestionPipeline:
    """Get or create ingestor instance."""
    global ingestor_instance
    if ingestor_instance is None:
        ingestor_instance = ModernIngestionPipeline()
    return ingestor_instance
