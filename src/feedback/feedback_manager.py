import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re
from collections import Counter

class FeedbackManager:
    def __init__(self, db_path: str = "data/feedback.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the feedback database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                message_id TEXT,
                feedback_type TEXT NOT NULL,
                rating INTEGER,
                comment TEXT,
                user_query TEXT,
                bot_response TEXT,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create feedback analytics table for caching
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value TEXT NOT NULL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON feedback(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rating ON feedback(rating)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON feedback(created_at)')
        
        conn.commit()
        conn.close()
    
    def add_feedback(self, session_id: str, feedback_type: str, rating: Optional[int] = None,
                    comment: Optional[str] = None, message_id: Optional[str] = None,
                    user_query: Optional[str] = None, bot_response: Optional[str] = None,
                    language: str = "en") -> str:
        """Add new feedback to the database"""
        feedback_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (id, session_id, message_id, feedback_type, rating, 
                                comment, user_query, bot_response, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (feedback_id, session_id, message_id, feedback_type, rating, 
              comment, user_query, bot_response, language))
        
        conn.commit()
        conn.close()
        
        # Trigger analytics recalculation for important metrics
        if rating is not None:
            self._update_rating_analytics()
        
        return feedback_id
    
    def get_feedback_analytics(self) -> Dict:
        """Get comprehensive feedback analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total feedback count
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cursor.fetchone()[0]
        
        # Average rating
        cursor.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
        avg_rating_result = cursor.fetchone()[0]
        average_rating = round(avg_rating_result, 2) if avg_rating_result else 0.0
        
        # Rating distribution
        cursor.execute('''
            SELECT rating, COUNT(*) 
            FROM feedback 
            WHERE rating IS NOT NULL 
            GROUP BY rating 
            ORDER BY rating
        ''')
        rating_dist = dict(cursor.fetchall())
        rating_distribution = {str(i): rating_dist.get(i, 0) for i in range(1, 6)}
        
        # Feedback by type
        cursor.execute('''
            SELECT feedback_type, COUNT(*) 
            FROM feedback 
            GROUP BY feedback_type
        ''')
        feedback_by_type = dict(cursor.fetchall())
        
        # Recent feedback (last 10)
        cursor.execute('''
            SELECT id, session_id, feedback_type, rating, comment, created_at
            FROM feedback 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        recent_feedback = []
        for row in cursor.fetchall():
            recent_feedback.append({
                'id': row[0],
                'session_id': row[1],
                'feedback_type': row[2],
                'rating': row[3],
                'comment': row[4],
                'created_at': row[5]
            })
        
        # Common issues from comments
        cursor.execute('SELECT comment FROM feedback WHERE comment IS NOT NULL AND comment != ""')
        comments = [row[0] for row in cursor.fetchall()]
        common_issues = self._extract_common_issues(comments)
        
        conn.close()
        
        return {
            'total_feedback': total_feedback,
            'average_rating': average_rating,
            'rating_distribution': rating_distribution,
            'feedback_by_type': feedback_by_type,
            'recent_feedback': recent_feedback,
            'common_issues': common_issues
        }
    
    def get_filtered_feedback(self, feedback_type: Optional[str] = None,
                            rating_min: Optional[int] = None, rating_max: Optional[int] = None,
                            date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
                            language: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get filtered feedback based on criteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM feedback WHERE 1=1'
        params = []
        
        if feedback_type:
            query += ' AND feedback_type = ?'
            params.append(feedback_type)
        
        if rating_min is not None:
            query += ' AND rating >= ?'
            params.append(rating_min)
        
        if rating_max is not None:
            query += ' AND rating <= ?'
            params.append(rating_max)
        
        if date_from:
            query += ' AND created_at >= ?'
            params.append(date_from.isoformat())
        
        if date_to:
            query += ' AND created_at <= ?'
            params.append(date_to.isoformat())
        
        if language:
            query += ' AND language = ?'
            params.append(language)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        columns = [description[0] for description in cursor.description]
        feedback_list = []
        for row in cursor.fetchall():
            feedback_dict = dict(zip(columns, row))
            feedback_list.append(feedback_dict)
        
        conn.close()
        return feedback_list
    
    def get_session_feedback(self, session_id: str) -> List[Dict]:
        """Get all feedback for a specific session"""
        return self.get_filtered_feedback(limit=1000, offset=0)
    
    def _extract_common_issues(self, comments: List[str], top_n: int = 5) -> List[str]:
        """Extract common issues from feedback comments using keyword analysis"""
        if not comments:
            return []
        
        # Common issue keywords and patterns
        issue_patterns = {
            'slow response': r'\b(slow|delay|wait|timeout|loading)\b',
            'incorrect information': r'\b(wrong|incorrect|inaccurate|mistake|error)\b',
            'navigation issues': r'\b(navigation|navigate|find|search|lost|confus)\b',
            'language problems': r'\b(language|translation|understand|unclear)\b',
            'technical errors': r'\b(error|crash|bug|broken|fail|problem)\b'
        }
        
        issue_counts = Counter()
        
        for comment in comments:
            comment_lower = comment.lower()
            for issue_type, pattern in issue_patterns.items():
                if re.search(pattern, comment_lower):
                    issue_counts[issue_type] += 1
        
        # Return top issues
        common_issues = [issue for issue, count in issue_counts.most_common(top_n)]
        return common_issues
    
    def _update_rating_analytics(self):
        """Update cached rating analytics for performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear old analytics
        cursor.execute('DELETE FROM feedback_analytics WHERE metric_name LIKE "rating_%"')
        
        # Calculate and cache new analytics
        cursor.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
        avg_rating = cursor.fetchone()[0]
        
        if avg_rating:
            cursor.execute('''
                INSERT INTO feedback_analytics (metric_name, metric_value)
                VALUES (?, ?)
            ''', ('rating_average', str(round(avg_rating, 2))))
        
        conn.commit()
        conn.close()
    
    def get_feedback_trends(self, days: int = 30) -> Dict:
        """Get feedback trends over the specified number of days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Daily feedback count
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM feedback 
            WHERE created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (date_threshold,))
        
        daily_counts = dict(cursor.fetchall())
        
        # Daily average rating
        cursor.execute('''
            SELECT DATE(created_at) as date, AVG(rating) as avg_rating
            FROM feedback 
            WHERE created_at >= ? AND rating IS NOT NULL
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (date_threshold,))
        
        daily_ratings = {date: round(rating, 2) for date, rating in cursor.fetchall()}
        
        conn.close()
        
        return {
            'daily_feedback_count': daily_counts,
            'daily_average_rating': daily_ratings,
            'period_days': days
        }
