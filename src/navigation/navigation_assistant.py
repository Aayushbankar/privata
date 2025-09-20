#!/usr/bin/env python3
"""
Fast Navigation Assistant for MOSDAC AI Help Bot
===============================================

Lightweight, high-performance navigation assistance system
optimized for speed and minimal resource usage.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class NavigationStep:
    """Single navigation step"""
    step_number: int
    page_url: str
    page_title: str
    description: str
    action: str
    expected_elements: List[str]
    estimated_time: int  # seconds

@dataclass
class NavigationPath:
    """Complete navigation path"""
    intent: str
    goal: str
    steps: List[NavigationStep]
    total_time: int
    difficulty: str
    success_rate: float

class FastNavigationAssistant:
    """High-performance navigation assistant with cached responses"""
    
    def __init__(self):
        self.site_structure = self._load_mosdac_structure()
        self.intent_patterns = self._compile_intent_patterns()
        self.navigation_cache = {}
        
    @lru_cache(maxsize=1)
    def _load_mosdac_structure(self) -> Dict[str, Any]:
        """Load MOSDAC site structure (cached for performance)"""
        return {
            "home": {
                "url": "/",
                "title": "MOSDAC Home",
                "description": "Meteorological & Oceanographic Satellite Data Archival Centre",
                "key_elements": ["navigation_menu", "search_box", "featured_services"]
            },
            "satellites": {
                "insat-3d": {
                    "url": "/insat-3d",
                    "title": "INSAT-3D Satellite",
                    "description": "Weather monitoring satellite data and products",
                    "key_elements": ["data_products", "download_section", "documentation"]
                },
                "insat-3dr": {
                    "url": "/insat-3dr",
                    "title": "INSAT-3DR Satellite", 
                    "description": "Advanced weather satellite with improved capabilities",
                    "key_elements": ["data_products", "download_section", "technical_specs"]
                },
                "oceansat-2": {
                    "url": "/oceansat-2",
                    "title": "Oceansat-2 Satellite",
                    "description": "Ocean monitoring and coastal applications",
                    "key_elements": ["ocean_data", "coastal_products", "download_tools"]
                },
                "oceansat-3": {
                    "url": "/oceansat-3",
                    "title": "Oceansat-3 Satellite",
                    "description": "Latest ocean observation satellite",
                    "key_elements": ["latest_data", "ocean_products", "api_access"]
                }
            },
            "services": {
                "data-download": {
                    "url": "/data-download",
                    "title": "Data Download",
                    "description": "Download satellite data and products",
                    "key_elements": ["satellite_selector", "date_picker", "download_button"]
                },
                "weather-forecast": {
                    "url": "/weather-forecast",
                    "title": "Weather Forecast",
                    "description": "Weather predictions and forecasts",
                    "key_elements": ["location_selector", "forecast_maps", "time_selector"]
                },
                "live-frame": {
                    "url": "/live-frame",
                    "title": "MOSDAC Live",
                    "description": "Real-time satellite imagery and data",
                    "key_elements": ["live_imagery", "animation_controls", "layer_selector"]
                }
            },
            "tools": {
                "api-access": {
                    "url": "/api-access",
                    "title": "API Access",
                    "description": "Programmatic access to MOSDAC data",
                    "key_elements": ["api_documentation", "authentication", "endpoints"]
                },
                "data-visualization": {
                    "url": "/visualization",
                    "title": "Data Visualization",
                    "description": "Interactive data visualization tools",
                    "key_elements": ["chart_tools", "map_viewer", "export_options"]
                }
            }
        }
    
    def _compile_intent_patterns(self) -> Dict[str, List[str]]:
        """Compile regex patterns for fast intent detection"""
        return {
            "download": [
                r"\b(download|get|access|retrieve|obtain)\b.*\b(data|satellite|image|product)\b",
                r"\b(how to|where to|can I)\b.*\b(download|get)\b",
                r"\b(data download|file download|satellite download)\b"
            ],
            "view": [
                r"\b(view|see|show|display|look at)\b.*\b(satellite|image|data|map)\b",
                r"\b(live|real-time|current)\b.*\b(imagery|data|satellite)\b",
                r"\b(visualization|visualize|plot|chart)\b"
            ],
            "find": [
                r"\b(find|search|locate|where is)\b.*\b(satellite|data|service)\b",
                r"\b(which satellite|what satellite)\b",
                r"\b(search for|looking for)\b"
            ],
            "weather": [
                r"\b(weather|forecast|prediction|climate)\b",
                r"\b(temperature|rainfall|wind|humidity)\b",
                r"\b(meteorological|atmospheric)\b"
            ],
            "ocean": [
                r"\b(ocean|sea|marine|coastal)\b.*\b(data|monitoring|observation)\b",
                r"\b(oceansat|sea surface|wave height)\b",
                r"\b(coastal|marine environment)\b"
            ],
            "api": [
                r"\b(api|programmatic|automated|script)\b.*\b(access|download|retrieve)\b",
                r"\b(rest api|web service|endpoint)\b",
                r"\b(authentication|token|key)\b"
            ]
        }
    
    @lru_cache(maxsize=500)
    def detect_navigation_intent(self, query: str) -> Tuple[str, float]:
        """Fast intent detection with caching"""
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            
            if score > 0:
                intent_scores[intent] = score / len(patterns)
        
        if not intent_scores:
            return "browse", 0.3
        
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent[0], best_intent[1]
    
    def generate_navigation_path(self, intent: str, query: str) -> NavigationPath:
        """Generate optimized navigation path based on intent"""
        cache_key = f"{intent}:{hash(query)}"
        
        if cache_key in self.navigation_cache:
            return self.navigation_cache[cache_key]
        
        path = self._create_navigation_path(intent, query)
        self.navigation_cache[cache_key] = path
        
        return path
    
    def _create_navigation_path(self, intent: str, query: str) -> NavigationPath:
        """Create navigation path based on intent"""
        paths = {
            "download": self._create_download_path(query),
            "view": self._create_view_path(query),
            "find": self._create_search_path(query),
            "weather": self._create_weather_path(query),
            "ocean": self._create_ocean_path(query),
            "api": self._create_api_path(query),
            "browse": self._create_browse_path(query)
        }
        
        return paths.get(intent, paths["browse"])
    
    def _create_download_path(self, query: str) -> NavigationPath:
        """Create path for data download"""
        steps = [
            NavigationStep(
                step_number=1,
                page_url="/",
                page_title="MOSDAC Home",
                description="Start from MOSDAC homepage",
                action="Navigate to homepage and locate the main navigation menu",
                expected_elements=["navigation_menu", "services_section"],
                estimated_time=5
            ),
            NavigationStep(
                step_number=2,
                page_url="/data-download",
                page_title="Data Download",
                description="Access the data download section",
                action="Click on 'Data Download' or 'Services' → 'Data Download'",
                expected_elements=["satellite_selector", "date_picker"],
                estimated_time=10
            ),
            NavigationStep(
                step_number=3,
                page_url="/data-download",
                page_title="Select Data Parameters",
                description="Choose satellite, date range, and data type",
                action="Select desired satellite, date range, and data products",
                expected_elements=["parameter_form", "preview_section"],
                estimated_time=30
            ),
            NavigationStep(
                step_number=4,
                page_url="/data-download",
                page_title="Download Data",
                description="Complete the download process",
                action="Click 'Download' button and save the file",
                expected_elements=["download_button", "progress_indicator"],
                estimated_time=60
            )
        ]
        
        return NavigationPath(
            intent="download",
            goal="Download satellite data from MOSDAC",
            steps=steps,
            total_time=105,
            difficulty="Medium",
            success_rate=0.85
        )
    
    def _create_view_path(self, query: str) -> NavigationPath:
        """Create path for viewing data/imagery"""
        steps = [
            NavigationStep(
                step_number=1,
                page_url="/",
                page_title="MOSDAC Home",
                description="Start from MOSDAC homepage",
                action="Navigate to homepage",
                expected_elements=["navigation_menu", "live_imagery_section"],
                estimated_time=5
            ),
            NavigationStep(
                step_number=2,
                page_url="/live-frame",
                page_title="MOSDAC Live",
                description="Access real-time satellite imagery",
                action="Click on 'MOSDAC Live' or 'Live Frame'",
                expected_elements=["live_imagery", "animation_controls"],
                estimated_time=15
            ),
            NavigationStep(
                step_number=3,
                page_url="/live-frame",
                page_title="View Imagery",
                description="Explore satellite imagery and controls",
                action="Use animation controls and layer selector to view different data",
                expected_elements=["layer_selector", "time_controls", "zoom_controls"],
                estimated_time=45
            )
        ]
        
        return NavigationPath(
            intent="view",
            goal="View real-time satellite imagery",
            steps=steps,
            total_time=65,
            difficulty="Easy",
            success_rate=0.95
        )
    
    def _create_search_path(self, query: str) -> NavigationPath:
        """Create path for searching/finding information"""
        steps = [
            NavigationStep(
                step_number=1,
                page_url="/",
                page_title="MOSDAC Home",
                description="Start from MOSDAC homepage",
                action="Navigate to homepage and locate search functionality",
                expected_elements=["search_box", "navigation_menu"],
                estimated_time=5
            ),
            NavigationStep(
                step_number=2,
                page_url="/search",
                page_title="Search Results",
                description="Use search functionality",
                action="Enter search terms and click search",
                expected_elements=["search_results", "filters"],
                estimated_time=20
            )
        ]
        
        return NavigationPath(
            intent="find",
            goal="Search for specific information or data",
            steps=steps,
            total_time=25,
            difficulty="Easy",
            success_rate=0.90
        )
    
    def _create_weather_path(self, query: str) -> NavigationPath:
        """Create path for weather-related queries"""
        steps = [
            NavigationStep(
                step_number=1,
                page_url="/",
                page_title="MOSDAC Home",
                description="Start from MOSDAC homepage",
                action="Navigate to homepage",
                expected_elements=["navigation_menu", "weather_section"],
                estimated_time=5
            ),
            NavigationStep(
                step_number=2,
                page_url="/weather-forecast",
                page_title="Weather Forecast",
                description="Access weather forecasting tools",
                action="Click on 'Weather Forecast' or 'Services' → 'Weather'",
                expected_elements=["location_selector", "forecast_maps"],
                estimated_time=15
            ),
            NavigationStep(
                step_number=3,
                page_url="/weather-forecast",
                page_title="View Weather Data",
                description="Explore weather forecasts and maps",
                action="Select location and view weather predictions",
                expected_elements=["weather_maps", "forecast_data", "time_selector"],
                estimated_time=30
            )
        ]
        
        return NavigationPath(
            intent="weather",
            goal="Access weather forecasts and meteorological data",
            steps=steps,
            total_time=50,
            difficulty="Easy",
            success_rate=0.92
        )
    
    def _create_ocean_path(self, query: str) -> NavigationPath:
        """Create path for ocean-related queries"""
        steps = [
            NavigationStep(
                step_number=1,
                page_url="/",
                page_title="MOSDAC Home",
                description="Start from MOSDAC homepage",
                action="Navigate to homepage",
                expected_elements=["navigation_menu", "ocean_section"],
                estimated_time=5
            ),
            NavigationStep(
                step_number=2,
                page_url="/oceansat-3",
                page_title="Oceansat-3 Data",
                description="Access ocean satellite data",
                action="Click on 'Oceansat-3' or navigate to ocean data section",
                expected_elements=["ocean_data", "coastal_products"],
                estimated_time=15
            ),
            NavigationStep(
                step_number=3,
                page_url="/oceansat-3",
                page_title="Explore Ocean Data",
                description="Browse ocean monitoring data and products",
                action="Explore available ocean data products and tools",
                expected_elements=["data_products", "download_tools", "visualization"],
                estimated_time=40
            )
        ]
        
        return NavigationPath(
            intent="ocean",
            goal="Access ocean monitoring data and coastal applications",
            steps=steps,
            total_time=60,
            difficulty="Medium",
            success_rate=0.88
        )
    
    def _create_api_path(self, query: str) -> NavigationPath:
        """Create path for API access"""
        steps = [
            NavigationStep(
                step_number=1,
                page_url="/",
                page_title="MOSDAC Home",
                description="Start from MOSDAC homepage",
                action="Navigate to homepage",
                expected_elements=["navigation_menu", "developer_section"],
                estimated_time=5
            ),
            NavigationStep(
                step_number=2,
                page_url="/api-access",
                page_title="API Documentation",
                description="Access API documentation and tools",
                action="Click on 'API Access' or 'Developer Tools'",
                expected_elements=["api_documentation", "authentication_section"],
                estimated_time=20
            ),
            NavigationStep(
                step_number=3,
                page_url="/api-access",
                page_title="Setup API Access",
                description="Configure API authentication and test endpoints",
                action="Follow authentication setup and test API endpoints",
                expected_elements=["api_key_section", "endpoint_tester", "code_examples"],
                estimated_time=120
            )
        ]
        
        return NavigationPath(
            intent="api",
            goal="Setup programmatic access to MOSDAC data",
            steps=steps,
            total_time=145,
            difficulty="Hard",
            success_rate=0.75
        )
    
    def _create_browse_path(self, query: str) -> NavigationPath:
        """Create general browsing path"""
        steps = [
            NavigationStep(
                step_number=1,
                page_url="/",
                page_title="MOSDAC Home",
                description="Explore MOSDAC homepage",
                action="Browse the homepage to understand available services",
                expected_elements=["navigation_menu", "featured_services", "recent_updates"],
                estimated_time=30
            ),
            NavigationStep(
                step_number=2,
                page_url="/sitemap",
                page_title="Site Map",
                description="View complete site structure",
                action="Click on 'Sitemap' to see all available sections",
                expected_elements=["site_structure", "section_links"],
                estimated_time=15
            )
        ]
        
        return NavigationPath(
            intent="browse",
            goal="General exploration of MOSDAC portal",
            steps=steps,
            total_time=45,
            difficulty="Easy",
            success_rate=0.98
        )
    
    def get_navigation_guidance(self, query: str) -> Dict[str, Any]:
        """Main method to get navigation guidance"""
        intent, confidence = self.detect_navigation_intent(query)
        path = self.generate_navigation_path(intent, query)
        
        return {
            "query": query,
            "intent": intent,
            "confidence": confidence,
            "navigation_path": {
                "goal": path.goal,
                "total_steps": len(path.steps),
                "estimated_time": path.total_time,
                "difficulty": path.difficulty,
                "success_rate": path.success_rate,
                "steps": [
                    {
                        "step": step.step_number,
                        "page_url": step.page_url,
                        "page_title": step.page_title,
                        "description": step.description,
                        "action": step.action,
                        "expected_elements": step.expected_elements,
                        "estimated_time": step.estimated_time
                    }
                    for step in path.steps
                ]
            },
            "quick_tips": self._generate_quick_tips(intent),
            "alternative_paths": self._get_alternative_paths(intent),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_quick_tips(self, intent: str) -> List[str]:
        """Generate quick tips based on intent"""
        tips = {
            "download": [
                "Ensure you have sufficient storage space before downloading large datasets",
                "Check data availability for your desired date range first",
                "Consider using the API for automated downloads of multiple files"
            ],
            "view": [
                "Use browser zoom controls for better image detail",
                "Try different time animations to see data changes",
                "Bookmark frequently viewed imagery for quick access"
            ],
            "find": [
                "Use specific satellite names or data types in your search",
                "Check the FAQ section for common questions",
                "Browse by satellite mission for organized data access"
            ],
            "weather": [
                "Weather forecasts are updated multiple times daily",
                "Use the time slider to see forecast progression",
                "Compare different weather parameters for comprehensive analysis"
            ],
            "ocean": [
                "Ocean data includes sea surface temperature, wave height, and currents",
                "Coastal applications have specialized products for nearshore areas",
                "Check data quality flags before analysis"
            ],
            "api": [
                "Read the API documentation thoroughly before implementation",
                "Test endpoints with small requests first",
                "Implement proper error handling for robust applications"
            ]
        }
        
        return tips.get(intent, [
            "Explore the homepage to familiarize yourself with available services",
            "Use the site search function to find specific information",
            "Check the help section for detailed user guides"
        ])
    
    def _get_alternative_paths(self, intent: str) -> List[str]:
        """Get alternative navigation approaches"""
        alternatives = {
            "download": [
                "Use the API for programmatic downloads",
                "Browse by satellite mission first, then download",
                "Check the bulk download tools for large datasets"
            ],
            "view": [
                "Try the mobile-friendly viewer for basic viewing",
                "Use the advanced visualization tools for detailed analysis",
                "Check the gallery section for featured imagery"
            ],
            "find": [
                "Browse by categories instead of searching",
                "Use the advanced search filters",
                "Check the recently updated section"
            ]
        }
        
        return alternatives.get(intent, [
            "Use the main navigation menu for structured browsing",
            "Try the site search for specific topics",
            "Check the help documentation"
        ])

# Global instance for fast access
navigation_assistant = FastNavigationAssistant()
