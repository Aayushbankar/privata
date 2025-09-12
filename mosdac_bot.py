#!/usr/bin/env python3
"""
MOSDAC AI Help Bot - Master Control File
========================================

This is the master file that orchestrates all existing components:
1. Uses existing crawl4ai_mosdac.py for scraping
2. Uses existing ingest.py for data ingestion
3. Uses existing chat.py for AI chat
4. Provides unified control interface

Author: AI Assistant
Date: 2025-01-10
Version: 1.0
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MOSDACBot:
    """Master control for MOSDAC AI Help Bot using existing components"""
    
    def __init__(self):
        # Configuration
        self.crawl_output_dir = Path("./mosdac_complete_data")
        self.chroma_dir = Path("./chroma_db")
        self.llm_available = False
        
        # Check if components are available
        self.check_components()
    
    def check_components(self):
        """Check if all required components are available"""
        components = {
            "crawler": Path("crawl4ai_mosdac.py").exists(),
            "ingest": Path("ingest.py").exists(),
            "chat": Path("chat.py").exists(),
            "config": Path("config.py").exists(),
            "llm_loader": Path("models/llm_loader.py").exists()
        }
        
        missing = [name for name, exists in components.items() if not exists]
        if missing:
            logger.warning(f"Missing components: {missing}")
        
        # Check if LLM is available
        try:
            from models.llm_loader import get_llm_info
            info = get_llm_info()
            self.llm_available = info.get("available", False)
            if self.llm_available:
                mode = info.get("mode", "unknown")
                logger.info(f"✅ LLM is available (mode: {mode})")
            else:
                mode = info.get("mode", "unknown")
                logger.warning(f"❌ LLM not available (mode: {mode})")
        except Exception as e:
            self.llm_available = False
            logger.warning(f"❌ LLM not available: {e}")
    
    async def scrape_data(self):
        """Run the comprehensive scraper to scrape ALL MOSDAC data"""
        logger.info("🔍 Starting comprehensive data scraping...")
        
        try:
            # Import and run the comprehensive scraper
            from comprehensive_mosdac_scraper import ComprehensiveMOSDACScraper
            
            # Use comprehensive scraper
            scraper = ComprehensiveMOSDACScraper()
            stats = await scraper.run_comprehensive_scraping()
            
            if stats["urls_processed"] > 0:
                logger.info("✅ Comprehensive scraping completed successfully!")
                logger.info(f"📊 Processed: {stats['urls_processed']} URLs")
                logger.info(f"📄 Total content: {stats['total_content_length']:,} characters")
                logger.info(f"📊 Tables extracted: {stats['tables_extracted']}")
                return True
            else:
                logger.error("❌ No URLs were processed successfully!")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error during comprehensive scraping: {e}")
            return False
    
    def ingest_data(self):
        """Run the existing ingestion pipeline with comprehensive data"""
        logger.info("📥 Starting data ingestion...")
        
        try:
            # Import and run the existing ingestion
            from ingest import ModernIngestionPipeline
            
            # Use the comprehensive data directory
            path = str(self.crawl_output_dir)
            
            logger.info(f"Ingesting from: {path}")
            
            # Check if comprehensive data exists
            if not self.crawl_output_dir.exists():
                logger.error(f"❌ Comprehensive data directory not found: {path}")
                logger.info("💡 Run comprehensive scraping first (option 1)")
                return False
            
            # Create and run ingestion pipeline
            pipeline = ModernIngestionPipeline()
            result = pipeline.run_ingestion(path)
            
            if result.get("success", False):
                logger.info("✅ Data ingestion completed successfully!")
                logger.info(f"📊 Documents: {result.get('documents_loaded', 0)}")
                logger.info(f"📄 Chunks: {result.get('chunks_stored', 0)}")
                logger.info(f"⏱️ Time: {result.get('processing_time', 0):.2f}s")
                return True
            else:
                logger.error(f"❌ Data ingestion failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during ingestion: {e}")
            return False
    
    def start_chat(self):
        """Start the existing chat system"""
        logger.info("💬 Starting chat system...")
        
        if not self.llm_available:
            print("❌ LLM not available. Please check your configuration:")
            print("   • For API mode: Set GEMINI_API_KEY environment variable")
            print("   • For Ollama mode: Set LLM_MODE=ollama and ensure Ollama is running")
            return
        
        try:
            # Import and start the existing chat system
            from chat import start_modern_chat
            start_modern_chat()
            
        except Exception as e:
            logger.error(f"❌ Error starting chat: {e}")
            print(f"Error: {e}")
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get current data status"""
        status = {
            "scraped_data": {
                "pages_count": 0,
                "total_content_length": 0,
                "last_scraped": None
            },
            "vector_database": {
                "collection_exists": False,
                "document_count": 0
            },
            "components": {
                "crawler_available": Path("crawl4ai_mosdac.py").exists(),
                "ingest_available": Path("ingest.py").exists(),
                "chat_available": Path("chat.py").exists(),
                "llm_available": self.llm_available
            }
        }
        
        # Check scraped data
        if self.crawl_output_dir.exists():
            # Try comprehensive index first, then fallback to crawling summary
            summary_file = self.crawl_output_dir / "comprehensive_index.json"
            if not summary_file.exists():
                summary_file = self.crawl_output_dir / "crawling_summary.json"
            
            if summary_file.exists():
                try:
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                        # Handle both comprehensive_index.json and crawling_summary.json formats
                        if "statistics" in summary:
                            # Comprehensive index format
                            stats = summary.get("statistics", {})
                            status["scraped_data"]["pages_count"] = stats.get("urls_processed", 0)
                            status["scraped_data"]["last_scraped"] = summary.get("metadata", {}).get("scraping_session", {}).get("completed_at")
                            status["scraped_data"]["total_content_length"] = stats.get("total_content_length", 0)
                        else:
                            # Crawling summary format
                            status["scraped_data"]["pages_count"] = summary.get("total_pages", 0)
                            status["scraped_data"]["last_scraped"] = summary.get("crawling_completed_at") or summary.get("timestamp")
                        
                        # Calculate total content length
                        total_length = 0
                        for page_dir in self.crawl_output_dir.iterdir():
                            if page_dir.is_dir():
                                content_file = page_dir / "content.md"
                                if content_file.exists():
                                    total_length += len(content_file.read_text())
                        status["scraped_data"]["total_content_length"] = total_length
                except Exception as e:
                    logger.warning(f"Failed to read summary file: {e}")
            else:
                # Count pages manually if no summary file
                page_count = 0
                total_length = 0
                for page_dir in self.crawl_output_dir.iterdir():
                    if page_dir.is_dir():
                        page_count += 1
                        content_file = page_dir / "content.md"
                        if content_file.exists():
                            total_length += len(content_file.read_text())
                status["scraped_data"]["pages_count"] = page_count
                status["scraped_data"]["total_content_length"] = total_length
        
        # Check vector database
        if self.chroma_dir.exists():
            try:
                import chromadb
                client = chromadb.PersistentClient(path=str(self.chroma_dir))
                collections = client.list_collections()
                if collections:
                    status["vector_database"]["collection_exists"] = True
                    # Try to get document count
                    try:
                        collection = client.get_collection("mosdac_collection")
                        count = collection.count()
                        status["vector_database"]["document_count"] = count
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Failed to check vector database: {e}")
        
        return status
    
    def _get_llm_info(self) -> Dict[str, Any]:
        """Get LLM configuration info"""
        try:
            from models.llm_loader import get_llm_info
            return get_llm_info()
        except Exception as e:
            return {
                "mode": "unknown",
                "available": False,
                "error": str(e)
            }
    
    def remove_data(self):
        """Remove all scraped data and vector database"""
        logger.info("🗑️ Removing all data...")
        
        # Remove scraped data
        if self.crawl_output_dir.exists():
            import shutil
            shutil.rmtree(self.crawl_output_dir)
            logger.info("✅ Removed scraped data")
        
        # Remove vector database
        if self.chroma_dir.exists():
            import shutil
            shutil.rmtree(self.chroma_dir)
            logger.info("✅ Removed vector database")
        
        # Recreate crawl output directory
        self.crawl_output_dir.mkdir(exist_ok=True)
        
        logger.info("✅ Data removal completed")
    
    def scrape_and_ingest(self):
        """Complete workflow: scrape and ingest data"""
        logger.info("🚀 Starting complete workflow: scrape + ingest")
        
        # Step 1: Scrape data
        scrape_success = asyncio.run(self.scrape_data())
        if not scrape_success:
            logger.error("❌ Scraping failed, aborting workflow")
            return False
        
        # Step 2: Ingest data
        ingest_success = self.ingest_data()
        if not ingest_success:
            logger.error("❌ Ingestion failed")
            return False
        
        logger.info("✅ Complete workflow finished successfully!")
        return True

def show_menu():
    """Show main menu"""
    print("\n" + "="*60)
    print("🛰️  MOSDAC AI Help Bot - Master Control")
    print("="*60)
    print("[1] 🔍 Scrape Data Only")
    print("[2] 📥 Ingest Data Only")
    print("[3] 🚀 Scrape + Ingest (Complete Workflow)")
    print("[4] 💬 Chat with Bot")
    print("[5] 📊 Check Data Status")
    print("[6] 🗑️  Remove All Data")
    print("[7] 🔄 Re-scrape + Re-ingest")
    print("[8] ❌ Exit")
    print("="*60)

async def main():
    """Main function"""
    bot = MOSDACBot()
    
    while True:
        show_menu()
        choice = input("Select an option (1-8): ").strip()
        
        if choice == "1":
            print("\n🔍 Starting data scraping...")
            success = await bot.scrape_data()
            if success:
                print("✅ Data scraping completed successfully!")
            else:
                print("❌ Data scraping failed!")
        
        elif choice == "2":
            print("\n📥 Starting data ingestion...")
            success = bot.ingest_data()
            if success:
                print("✅ Data ingestion completed successfully!")
            else:
                print("❌ Data ingestion failed!")
        
        elif choice == "3":
            print("\n🚀 Starting complete workflow...")
            success = bot.scrape_and_ingest()
            if success:
                print("✅ Complete workflow finished successfully!")
            else:
                print("❌ Workflow failed!")
        
        elif choice == "4":
            print("\n💬 Starting chat mode...")
            bot.start_chat()
        
        elif choice == "5":
            print("\n📊 Current Data Status:")
            status = bot.get_data_status()
            llm_info = bot._get_llm_info()
            
            print(f"📄 Scraped Data:")
            print(f"   Pages: {status['scraped_data']['pages_count']}")
            print(f"   Total Content: {status['scraped_data']['total_content_length']:,} characters")
            print(f"   Last Scraped: {status['scraped_data']['last_scraped'] or 'Never'}")
            
            print(f"\n🗄️  Vector Database:")
            print(f"   Collection Exists: {status['vector_database']['collection_exists']}")
            print(f"   Documents: {status['vector_database']['document_count']}")
            
            print(f"\n🤖 LLM Configuration:")
            print(f"   Mode: {llm_info.get('mode', 'unknown')}")
            if llm_info.get('mode') == 'api':
                print(f"   API Key: {'✅ Set' if llm_info.get('api_key_set') else '❌ Missing'}")
            elif llm_info.get('mode') == 'ollama':
                print(f"   Model: {llm_info.get('ollama_model', 'unknown')}")
                print(f"   URL: {llm_info.get('ollama_url', 'unknown')}")
            print(f"   Available: {'✅' if llm_info.get('available') else '❌'}")
            
            print(f"\n🔧 Components:")
            print(f"   Crawler: {'✅' if status['components']['crawler_available'] else '❌'}")
            print(f"   Ingest: {'✅' if status['components']['ingest_available'] else '❌'}")
            print(f"   Chat: {'✅' if status['components']['chat_available'] else '❌'}")
        
        elif choice == "6":
            confirm = input("⚠️  Are you sure you want to remove ALL data? (yes/no): ").strip().lower()
            if confirm == "yes":
                bot.remove_data()
                print("✅ All data removed successfully!")
            else:
                print("❌ Data removal cancelled.")
        
        elif choice == "7":
            print("\n🔄 Re-scraping and re-ingesting data...")
            bot.remove_data()
            success = bot.scrape_and_ingest()
            if success:
                print("✅ Re-scraping and re-ingestion completed successfully!")
            else:
                print("❌ Re-scraping and re-ingestion failed!")
        
        elif choice == "8":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())