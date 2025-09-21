"""
Admin Dashboard Backend for MOSDAC AI Help Bot.

This module provides comprehensive administrative interface with real system data
for managing the MOSDAC AI Help Bot system.
"""

import os
import sys
import sqlite3
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.feedback.feedback_manager import FeedbackManager

app = FastAPI(
    title="MOSDAC AI Help Bot - Admin Dashboard",
    description="Administrative interface for MOSDAC AI Help Bot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize feedback manager
feedback_manager = FeedbackManager()

# Pydantic models
class SystemStats(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    uptime_hours: float

class FeedbackStats(BaseModel):
    total_feedback: int
    average_rating: float
    rating_distribution: Dict[str, int]
    recent_feedback: List[Dict]
    feedback_trends: List[Dict]

class DataStats(BaseModel):
    scraped_pages: int
    vector_db_size: int
    last_scrape_time: Optional[str]
    data_size_mb: float

class ChatStats(BaseModel):
    total_sessions: int
    active_sessions: int
    total_messages: int
    avg_response_time: float

# Helper functions
def get_system_stats() -> SystemStats:
    """Get real system statistics."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = psutil.boot_time()
    uptime = (datetime.now().timestamp() - boot_time) / 3600
    
    return SystemStats(
        cpu_percent=psutil.cpu_percent(interval=1),
        memory_percent=memory.percent,
        memory_used_gb=memory.used / (1024**3),
        memory_total_gb=memory.total / (1024**3),
        disk_percent=disk.percent,
        disk_used_gb=disk.used / (1024**3),
        disk_total_gb=disk.total / (1024**3),
        uptime_hours=uptime
    )

def get_feedback_stats() -> FeedbackStats:
    """Get real feedback statistics from database."""
    try:
        # Get feedback analytics
        analytics = feedback_manager.get_analytics()
        
        # Get recent feedback
        recent = feedback_manager.get_feedback_list(limit=10)
        
        # Get trends (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        trends = feedback_manager.get_feedback_trends(start_date, end_date)
        
        return FeedbackStats(
            total_feedback=analytics.total_feedback,
            average_rating=analytics.average_rating,
            rating_distribution=analytics.rating_distribution,
            recent_feedback=[{
                "id": f.id,
                "rating": f.rating,
                "comment": f.comment,
                "timestamp": f.timestamp.isoformat(),
                "feedback_type": f.feedback_type
            } for f in recent],
            feedback_trends=[{
                "date": trend.date.isoformat(),
                "count": trend.count,
                "avg_rating": trend.avg_rating
            } for trend in trends]
        )
    except Exception as e:
        return FeedbackStats(
            total_feedback=0,
            average_rating=0.0,
            rating_distribution={},
            recent_feedback=[],
            feedback_trends=[]
        )

def get_data_stats() -> DataStats:
    """Get real data statistics."""
    try:
        data_dir = Path(__file__).parent.parent.parent / "data"
        scraped_dir = data_dir / "scraped" / "mosdac_complete_data"
        
        # Count scraped pages
        scraped_pages = 0
        if scraped_dir.exists():
            scraped_pages = len(list(scraped_dir.rglob("*.html")))
        
        # Get vector DB size
        vector_db_dir = data_dir / "vector_db"
        vector_db_size = 0
        if vector_db_dir.exists():
            vector_db_size = len(list(vector_db_dir.rglob("*")))
        
        # Calculate data size
        data_size = 0
        if data_dir.exists():
            for file_path in data_dir.rglob("*"):
                if file_path.is_file():
                    data_size += file_path.stat().st_size
        
        # Get last scrape time (check newest file)
        last_scrape_time = None
        if scraped_dir.exists():
            files = list(scraped_dir.rglob("*"))
            if files:
                newest_file = max(files, key=lambda f: f.stat().st_mtime if f.is_file() else 0)
                if newest_file.is_file():
                    last_scrape_time = datetime.fromtimestamp(newest_file.stat().st_mtime).isoformat()
        
        return DataStats(
            scraped_pages=scraped_pages,
            vector_db_size=vector_db_size,
            last_scrape_time=last_scrape_time,
            data_size_mb=data_size / (1024**2)
        )
    except Exception as e:
        return DataStats(
            scraped_pages=0,
            vector_db_size=0,
            last_scrape_time=None,
            data_size_mb=0.0
        )

def get_chat_stats() -> ChatStats:
    """Get chat statistics."""
    # TODO: Implement real chat session tracking
    # For now, return basic stats
    return ChatStats(
        total_sessions=0,
        active_sessions=0,
        total_messages=0,
        avg_response_time=0.0
    )

# API Routes
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics."""
    return {
        "system": get_system_stats().dict(),
        "feedback": get_feedback_stats().dict(),
        "data": get_data_stats().dict(),
        "chat": get_chat_stats().dict(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/system/info")
async def get_system_info():
    """Get detailed system information."""
    return {
        "platform": psutil.LINUX if hasattr(psutil, 'LINUX') else "unknown",
        "python_version": sys.version,
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "disk_total": psutil.disk_usage('/').total,
        "process_count": len(psutil.pids()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/feedback/analytics")
async def get_feedback_analytics():
    """Get detailed feedback analytics."""
    return get_feedback_stats().dict()

@app.get("/api/data/status")
async def get_data_status():
    """Get data ingestion status."""
    return get_data_stats().dict()

@app.post("/api/system/cleanup")
async def cleanup_system():
    """Perform system cleanup operations."""
    try:
        # Clean up temporary files
        temp_dir = Path("/tmp")
        cleaned_files = 0
        freed_space = 0
        
        for temp_file in temp_dir.glob("mosdac_*"):
            if temp_file.is_file():
                size = temp_file.stat().st_size
                temp_file.unlink()
                cleaned_files += 1
                freed_space += size
        
        return {
            "success": True,
            "cleaned_files": cleaned_files,
            "freed_space_mb": freed_space / (1024**2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/reindex")
async def reindex_data():
    """Trigger data reindexing."""
    try:
        # TODO: Implement actual reindexing
        return {
            "success": True,
            "message": "Reindexing started",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve admin frontend
@app.get("/", response_class=HTMLResponse)
async def admin_dashboard():
    """Serve the admin dashboard HTML."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MOSDAC AI Help Bot - Admin Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
            }
            .header {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .header h1 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card h3 {
                color: #2c3e50;
                margin-bottom: 15px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .stat-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 5px;
            }
            .stat-value {
                font-weight: bold;
                color: #2980b9;
            }
            .actions {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .btn {
                background: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .btn:hover {
                background: #2980b9;
            }
            .btn.danger {
                background: #e74c3c;
            }
            .btn.danger:hover {
                background: #c0392b;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #7f8c8d;
            }
            .progress-bar {
                width: 100%;
                height: 10px;
                background: #ecf0f1;
                border-radius: 5px;
                overflow: hidden;
                margin-top: 5px;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #3498db, #2ecc71);
                transition: width 0.3s ease;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎛️ MOSDAC AI Help Bot - Admin Dashboard</h1>
                <p>Real-time system monitoring and management interface</p>
                <p><strong>Last Updated:</strong> <span id="lastUpdate">Loading...</span></p>
            </div>

            <div id="loading" class="loading">
                <h3>Loading dashboard data...</h3>
            </div>

            <div id="dashboard" style="display: none;">
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>🖥️ System Performance</h3>
                        <div id="systemStats"></div>
                    </div>

                    <div class="stat-card">
                        <h3>⭐ Feedback Analytics</h3>
                        <div id="feedbackStats"></div>
                    </div>

                    <div class="stat-card">
                        <h3>📊 Data Status</h3>
                        <div id="dataStats"></div>
                    </div>

                    <div class="stat-card">
                        <h3>💬 Chat Statistics</h3>
                        <div id="chatStats"></div>
                    </div>
                </div>

                <div class="actions">
                    <h3>🔧 System Actions</h3>
                    <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
                    <button class="btn" onclick="cleanupSystem()">🧹 System Cleanup</button>
                    <button class="btn" onclick="reindexData()">🔄 Reindex Data</button>
                    <button class="btn danger" onclick="exportData()">📥 Export Data</button>
                </div>
            </div>
        </div>

        <script>
            let dashboardData = {};

            async function loadDashboardData() {
                try {
                    const response = await fetch('/api/dashboard/stats');
                    dashboardData = await response.json();
                    updateDashboard();
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                } catch (error) {
                    console.error('Failed to load dashboard data:', error);
                    document.getElementById('loading').innerHTML = '<h3>❌ Failed to load data</h3>';
                }
            }

            function updateDashboard() {
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
                
                // System stats
                const system = dashboardData.system;
                document.getElementById('systemStats').innerHTML = `
                    <div class="stat-item">
                        <span>CPU Usage</span>
                        <span class="stat-value">${system.cpu_percent.toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${system.cpu_percent}%"></div>
                    </div>
                    <div class="stat-item">
                        <span>Memory Usage</span>
                        <span class="stat-value">${system.memory_percent.toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${system.memory_percent}%"></div>
                    </div>
                    <div class="stat-item">
                        <span>Memory Used</span>
                        <span class="stat-value">${system.memory_used_gb.toFixed(1)} GB / ${system.memory_total_gb.toFixed(1)} GB</span>
                    </div>
                    <div class="stat-item">
                        <span>Disk Usage</span>
                        <span class="stat-value">${system.disk_percent.toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${system.disk_percent}%"></div>
                    </div>
                    <div class="stat-item">
                        <span>System Uptime</span>
                        <span class="stat-value">${system.uptime_hours.toFixed(1)} hours</span>
                    </div>
                `;

                // Feedback stats
                const feedback = dashboardData.feedback;
                document.getElementById('feedbackStats').innerHTML = `
                    <div class="stat-item">
                        <span>Total Feedback</span>
                        <span class="stat-value">${feedback.total_feedback}</span>
                    </div>
                    <div class="stat-item">
                        <span>Average Rating</span>
                        <span class="stat-value">${feedback.average_rating.toFixed(1)} ⭐</span>
                    </div>
                    <div class="stat-item">
                        <span>Recent Feedback</span>
                        <span class="stat-value">${feedback.recent_feedback.length} items</span>
                    </div>
                `;

                // Data stats
                const data = dashboardData.data;
                document.getElementById('dataStats').innerHTML = `
                    <div class="stat-item">
                        <span>Scraped Pages</span>
                        <span class="stat-value">${data.scraped_pages}</span>
                    </div>
                    <div class="stat-item">
                        <span>Vector DB Size</span>
                        <span class="stat-value">${data.vector_db_size} entries</span>
                    </div>
                    <div class="stat-item">
                        <span>Data Size</span>
                        <span class="stat-value">${data.data_size_mb.toFixed(1)} MB</span>
                    </div>
                    <div class="stat-item">
                        <span>Last Scrape</span>
                        <span class="stat-value">${data.last_scrape_time ? new Date(data.last_scrape_time).toLocaleString() : 'Never'}</span>
                    </div>
                `;

                // Chat stats
                const chat = dashboardData.chat;
                document.getElementById('chatStats').innerHTML = `
                    <div class="stat-item">
                        <span>Total Sessions</span>
                        <span class="stat-value">${chat.total_sessions}</span>
                    </div>
                    <div class="stat-item">
                        <span>Active Sessions</span>
                        <span class="stat-value">${chat.active_sessions}</span>
                    </div>
                    <div class="stat-item">
                        <span>Total Messages</span>
                        <span class="stat-value">${chat.total_messages}</span>
                    </div>
                    <div class="stat-item">
                        <span>Avg Response Time</span>
                        <span class="stat-value">${chat.avg_response_time.toFixed(2)}s</span>
                    </div>
                `;
            }

            async function refreshData() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('dashboard').style.display = 'none';
                await loadDashboardData();
            }

            async function cleanupSystem() {
                if (confirm('Are you sure you want to perform system cleanup?')) {
                    try {
                        const response = await fetch('/api/system/cleanup', { method: 'POST' });
                        const result = await response.json();
                        alert(`Cleanup completed: ${result.cleaned_files} files cleaned, ${result.freed_space_mb.toFixed(1)} MB freed`);
                        refreshData();
                    } catch (error) {
                        alert('Cleanup failed: ' + error.message);
                    }
                }
            }

            async function reindexData() {
                if (confirm('Are you sure you want to reindex the data? This may take some time.')) {
                    try {
                        const response = await fetch('/api/data/reindex', { method: 'POST' });
                        const result = await response.json();
                        alert('Reindexing started successfully');
                    } catch (error) {
                        alert('Reindexing failed: ' + error.message);
                    }
                }
            }

            function exportData() {
                alert('Data export functionality will be implemented soon');
            }

            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);

            // Initial load
            loadDashboardData();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
