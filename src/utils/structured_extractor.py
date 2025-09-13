# privata/utils/structured_extractor.py

import re
from typing import List, Dict, Any
from datetime import datetime
import json
from bs4 import BeautifulSoup

class StructuredDataExtractor:
    """Structured data extraction for mission information, dates, tables, and key-value pairs"""
    
    def __init__(self):
        # Mission patterns for MOSDAC content
        self.mission_patterns = {
            "insat_3dr": r"INSAT-3D[R]?",
            "insat_3d": r"INSAT-3D",
            "kalpana_1": r"KALPANA-1",
            "megha_tropiques": r"MeghaTropiques",
            "saral_altika": r"SARAL-AltiKa",
            "oceansat_2": r"OCEANSAT-2",
            "oceansat_3": r"OCEANSAT-3",
            "scatsat_1": r"SCATSAT-1",
            "insat_3ds": r"INSAT-3DS"
        }
        
        # Date patterns
        self.date_patterns = [
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",  # MM-DD-YYYY, MM/DD/YYYY
            r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",     # YYYY-MM-DD, YYYY/MM/DD
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
            r"\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b"
        ]
        
        # Key-value patterns common in technical documents
        self.key_value_patterns = [
            r"([A-Z][a-zA-Z\s]+):\s*([^\n]+)",  # Title: Value
            r"([A-Z][a-zA-Z\s]+)\s*-\s*([^\n]+)",  # Title - Value
            r"(\w+)\s*=\s*([^\n]+)",  # key=value
        ]
    
    def extract_mission_info(self, content: str) -> Dict[str, Any]:
        """Extract mission-specific information from content"""
        mission_info = {
            "missions": [],
            "mission_dates": {},
            "mission_references": 0,
            "detailed_info": {}
        }
        
        # Find mission names
        for mission_name, pattern in self.mission_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                mission_info["missions"].append(mission_name.upper())
                mission_info["mission_references"] += len(matches)
                
                # Store detailed match info
                mission_info["detailed_info"][mission_name] = {
                    "count": len(matches),
                    "examples": list(set(matches))[:3]  # First 3 unique examples
                }
        
        # Extract dates and associate with missions if possible
        dates = self.extract_dates(content)
        mission_info["dates"] = dates
        
        # Try to associate dates with missions
        mission_info["mission_dates"] = self._associate_dates_with_missions(content, dates)
        
        return mission_info
    
    def extract_dates(self, content: str) -> List[Dict[str, Any]]:
        """Extract and normalize dates from content"""
        dates = []
        
        for pattern in self.date_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    # Try to parse and normalize the date
                    if isinstance(match, tuple):
                        match_str = " ".join(match)
                    else:
                        match_str = match
                    
                    # Basic normalization
                    normalized = self._normalize_date(match_str)
                    if normalized:
                        dates.append({
                            "original": match_str,
                            "normalized": normalized,
                            "iso_format": normalized.isoformat() if hasattr(normalized, 'isoformat') else str(normalized)
                        })
                except Exception as e:
                    # Skip invalid dates
                    continue
        
        return dates
    
    def _normalize_date(self, date_str: str) -> Any:
        """Normalize date string to datetime object"""
        try:
            # Common date formats
            formats = [
                "%Y-%m-%d",
                "%m-%d-%Y", 
                "%d-%m-%Y",
                "%Y/%m/%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%b %d, %Y",
                "%d %b %Y",
                "%B %d, %Y",
                "%d %B %Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If no format matched, return the string
            return date_str
            
        except Exception:
            return date_str
    
    def _associate_dates_with_missions(self, content: str, dates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Associate extracted dates with mission names"""
        associations = {}
        
        for mission_name in self.mission_patterns.keys():
            mission_pattern = self.mission_patterns[mission_name]
            mission_matches = list(re.finditer(mission_pattern, content, re.IGNORECASE))
            
            for mission_match in mission_matches:
                mission_start = mission_match.start()
                mission_end = mission_match.end()
                
                # Find dates near this mission mention
                nearby_dates = []
                for date_info in dates:
                    date_pos = content.find(date_info["original"])
                    if date_pos != -1 and abs(date_pos - mission_start) < 200:  # Within 200 chars
                        nearby_dates.append(date_info)
                
                if nearby_dates:
                    if mission_name not in associations:
                        associations[mission_name] = []
                    associations[mission_name].extend(nearby_dates)
        
        return associations
    
    def extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract and structure tables from content"""
        tables = []
        
        # HTML table extraction (if content contains HTML)
        if "<table" in content.lower():
            try:
                soup = BeautifulSoup(content, 'html.parser')
                html_tables = soup.find_all('table')
                
                for i, table in enumerate(html_tables):
                    table_data = self._parse_html_table(table)
                    table_data["source"] = "html"
                    table_data["table_index"] = i
                    tables.append(table_data)
            except Exception as e:
                print(f"[WARNING] HTML table parsing failed: {e}")
        
        # Markdown table extraction
        md_tables = self._extract_markdown_tables(content)
        tables.extend(md_tables)
        
        return tables
    
    def _parse_html_table(self, table) -> Dict[str, Any]:
        """Parse HTML table into structured data"""
        result = {
            "headers": [],
            "rows": [],
            "row_count": 0,
            "column_count": 0
        }
        
        # Extract headers from thead or first row
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
            result["headers"] = headers
        else:
            # Check first row for headers
            first_row = table.find('tr')
            if first_row:
                headers = [cell.get_text().strip() for cell in first_row.find_all(['th', 'td'])]
                result["headers"] = headers
        
        # Extract rows
        rows = []
        for row in table.find_all('tr'):
            cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
            if cells and cells != result["headers"]:  # Skip header row if already extracted
                rows.append(cells)
        
        result["rows"] = rows
        result["row_count"] = len(rows)
        result["column_count"] = len(rows[0]) if rows else 0
        
        return result
    
    def _extract_markdown_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract markdown format tables"""
        tables = []
        lines = content.split('\n')
        current_table = None
        
        for i, line in enumerate(lines):
            # Markdown table pattern: | col1 | col2 | col3 |
            if re.match(r'^\|.*\|$', line.strip()) and '---' not in line:
                if current_table is None:
                    current_table = {
                        "headers": [],
                        "rows": [],
                        "source": "markdown",
                        "start_line": i
                    }
                    # Parse header
                    headers = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                    current_table["headers"] = headers
                else:
                    # Parse row
                    row = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                    current_table["rows"].append(row)
            elif current_table is not None and not line.strip():
                # Empty line ends the table
                tables.append(current_table)
                current_table = None
        
        # Add the last table if exists
        if current_table is not None:
            tables.append(current_table)
        
        return tables
    
    def extract_key_value_pairs(self, content: str) -> Dict[str, Any]:
        """Extract key-value pairs from content"""
        key_values = {}
        
        for pattern in self.key_value_patterns:
            matches = re.findall(pattern, content)
            for key, value in matches:
                key_clean = key.strip()
                value_clean = value.strip()
                
                if key_clean and value_clean:
                    key_values[key_clean] = value_clean
        
        return key_values
    
    def extract_structured_data(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive structured data extraction"""
        structured_data = {
            "mission_info": self.extract_mission_info(content),
            "dates": self.extract_dates(content),
            "tables": self.extract_tables(content),
            "key_value_pairs": self.extract_key_value_pairs(content),
            "metadata": metadata or {}
        }
        
        # Add statistics
        structured_data["statistics"] = {
            "mission_count": len(structured_data["mission_info"]["missions"]),
            "date_count": len(structured_data["dates"]),
            "table_count": len(structured_data["tables"]),
            "key_value_count": len(structured_data["key_value_pairs"])
        }
        
        return structured_data

# Global instance for easy access
structured_extractor = StructuredDataExtractor()
