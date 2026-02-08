"""
Database Manager for Splitwise Analytics
Handles SQLite operations for expenses and sync metadata
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Get database connection for current request"""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE_PATH', 'splitwise_data.db')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database tables"""
    db_path = current_app.config.get('DATABASE_PATH', 'splitwise_data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            splitwise_id INTEGER UNIQUE NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'INR',
            date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            deleted_at TEXT,
            group_id INTEGER,
            group_name TEXT,
            category TEXT,
            ai_category TEXT,
            payer_id INTEGER,
            payer_name TEXT,
            user_share REAL NOT NULL,
            is_payment INTEGER DEFAULT 0,
            synced_at TEXT NOT NULL
        )
    ''')
    
    # Create sync metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_meta (
            id INTEGER PRIMARY KEY,
            last_sync_timestamp TEXT,
            last_updated_expense_date TEXT,
            total_expenses_synced INTEGER DEFAULT 0
        )
    ''')
    
    # Create categories table for AI categorization cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category_cache (
            id INTEGER PRIMARY KEY,
            description_hash TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Insert initial sync meta if not exists
    cursor.execute('SELECT COUNT(*) FROM sync_meta')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO sync_meta (last_sync_timestamp, total_expenses_synced)
            VALUES (NULL, 0)
        ''')
    
    conn.commit()
    conn.close()
    
    # Register close_db with app
    current_app.teardown_appcontext(close_db)


class DatabaseManager:
    """Manager class for database operations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or 'splitwise_data.db'
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_existing_expense_ids(self) -> set:
        """Get all existing Splitwise expense IDs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT splitwise_id FROM expenses')
        ids = {row['splitwise_id'] for row in cursor.fetchall()}
        conn.close()
        return ids
    
    def insert_expenses(self, expenses: List[Dict]) -> int:
        """Bulk insert expenses, skip duplicates"""
        if not expenses:
            return 0
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        inserted = 0
        for expense in expenses:
            try:
                cursor.execute('''
                    INSERT INTO expenses (
                        splitwise_id, description, amount, currency, date,
                        created_at, updated_at, deleted_at, group_id, group_name,
                        category, payer_id, payer_name, user_share, is_payment, synced_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    expense['splitwise_id'],
                    expense['description'],
                    expense['amount'],
                    expense.get('currency', 'INR'),
                    expense['date'],
                    expense['created_at'],
                    expense.get('updated_at'),
                    expense.get('deleted_at'),
                    expense.get('group_id'),
                    expense.get('group_name'),
                    expense.get('category'),
                    expense.get('payer_id'),
                    expense.get('payer_name'),
                    expense['user_share'],
                    expense.get('is_payment', 0),
                    datetime.now().isoformat()
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.IntegrityError:
                # If we are here, it means ID exists. 
                # Since we want to support re-sync (undelete), we should update deleted_at = NULL if needed
                # But simple INSERT failed. Let's do an UPDATE if it exists
                cursor.execute('''
                    UPDATE expenses SET 
                        deleted_at = NULL,
                        updated_at = ?,
                        description = ?,
                        amount = ?,
                        date = ?,
                        user_share = ?
                    WHERE splitwise_id = ?
                ''', (
                    datetime.now().isoformat(),
                    expense['description'],
                    expense['amount'],
                    expense['date'],
                    expense['user_share'],
                    expense['splitwise_id']
                ))
                # Count as inserted/updated? technically updated.
                continue
        
        conn.commit()
        conn.close()
        return inserted
    
    def update_expense_category(self, splitwise_id: int, category: str):
        """Update AI category for an expense"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE expenses SET ai_category = ? WHERE splitwise_id = ?
        ''', (category, splitwise_id))
        conn.commit()
        conn.close()
    
    def bulk_update_categories(self, updates: List[Dict]):
        """Bulk update AI categories"""
        conn = self._get_connection()
        cursor = conn.cursor()
        for update in updates:
            cursor.execute('''
                UPDATE expenses SET ai_category = ? WHERE splitwise_id = ?
            ''', (update['category'], update['splitwise_id']))
        conn.commit()
        conn.close()
    
    def get_uncategorized_expenses(self, filters: Dict = None) -> List[Dict]:
        """Get expenses without AI category, optional filters"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, splitwise_id, description FROM expenses
            WHERE ai_category IS NULL AND deleted_at IS NULL AND is_payment = 0
        '''
        params = []
        
        if filters:
            if filters.get('start_date'):
                query += ' AND date >= ?'
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += ' AND date <= ?'
                params.append(filters['end_date'])
            if filters.get('year'):
                query += " AND strftime('%Y', date) = ?"
                params.append(filters['year'])
            if filters.get('month'):
                query += " AND strftime('%m', date) = ?"
                params.append(filters['month'])
                
        cursor.execute(query, params)
        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return expenses
    
    def get_all_expenses(self, filters: Dict = None) -> List[Dict]:
        """Get all expenses with optional filters"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM expenses
            WHERE deleted_at IS NULL AND is_payment = 0
        '''
        params = []
        
        if filters:
            if filters.get('start_date'):
                query += ' AND date >= ?'
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += ' AND date <= ?'
                params.append(filters['end_date'])
            if filters.get('category'):
                query += ' AND (ai_category = ? OR category = ?)'
                params.extend([filters['category'], filters['category']])
            if filters.get('group_id'):
                query += ' AND group_id = ?'
                params.append(filters['group_id'])
        
        query += ' ORDER BY date DESC'
        
        cursor.execute(query, params)
        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return expenses
    
    def get_monthly_analytics(self, year: str = None) -> List[Dict]:
        """Get monthly expense breakdown"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(user_share) as total,
                COUNT(*) as count
            FROM expenses
            WHERE deleted_at IS NULL AND is_payment = 0
        '''
        params = []
        
        if year:
            query += " AND strftime('%Y', date) = ?"
            params.append(year)
        
        query += ' GROUP BY month ORDER BY month DESC'
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_yearly_analytics(self) -> List[Dict]:
        """Get yearly expense breakdown"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                strftime('%Y', date) as year,
                SUM(user_share) as total,
                COUNT(*) as count
            FROM expenses
            WHERE deleted_at IS NULL AND is_payment = 0
            GROUP BY year
            ORDER BY year DESC
        ''')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_category_breakdown(self, year: str = None, month: str = None) -> List[Dict]:
        """Get expense breakdown by category"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                CASE 
                    WHEN COALESCE(ai_category, category) IN ('Groceries', 'Grocery') THEN 'Grocery'
                    WHEN COALESCE(ai_category, category) = 'Dining out' THEN 'Food'
                    ELSE COALESCE(ai_category, category, 'Uncategorized')
                END as category_name,
                SUM(user_share) as total,
                COUNT(*) as count
            FROM expenses
            WHERE deleted_at IS NULL AND is_payment = 0
        '''
        params = []
        
        if year:
            query += " AND strftime('%Y', date) = ?"
            params.append(year)
        if month:
            query += " AND strftime('%m', date) = ?"
            params.append(month)
            
        query += ' GROUP BY category_name ORDER BY total DESC'
        
        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            res = dict(row)
            res['category'] = res['category_name'] # Map back for frontend
            del res['category_name']
            results.append(res)
            
        conn.close()
        return results
    
    def update_sync_meta(self, last_expense_date: str = None, count: int = 0):
        """Update sync metadata"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sync_meta SET
                last_sync_timestamp = ?,
                last_updated_expense_date = COALESCE(?, last_updated_expense_date),
                total_expenses_synced = total_expenses_synced + ?
            WHERE id = 1
        ''', (datetime.now().isoformat(), last_expense_date, count))
        conn.commit()
        conn.close()
    
    def get_sync_status(self) -> Dict:
        """Get sync status information"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get sync meta
        cursor.execute('SELECT * FROM sync_meta WHERE id = 1')
        sync_meta = dict(cursor.fetchone())
        
        # Get expense count
        cursor.execute('SELECT COUNT(*) as count FROM expenses WHERE deleted_at IS NULL')
        sync_meta['expense_count'] = cursor.fetchone()['count']
        
        conn.close()
        return sync_meta
    
    def cache_category(self, description: str, category: str):
        """Cache category for a description"""
        import hashlib
        desc_hash = hashlib.md5(description.lower().strip().encode()).hexdigest()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO category_cache (description_hash, description, category, created_at)
                VALUES (?, ?, ?, ?)
            ''', (desc_hash, description, category, datetime.now().isoformat()))
            conn.commit()
        except Exception:
            pass
        conn.close()
    
    def get_cached_category(self, description: str) -> Optional[str]:
        """Get cached category for a description"""
        import hashlib
        desc_hash = hashlib.md5(description.lower().strip().encode()).hexdigest()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT category FROM category_cache WHERE description_hash = ?', (desc_hash,))
        row = cursor.fetchone()
        conn.close()
        return row['category'] if row else None

    def delete_expense(self, expense_id: int) -> bool:
        """Soft delete an expense"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE expenses SET deleted_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), expense_id))
        
        row_count = cursor.rowcount
        conn.commit()
        conn.close()
        return row_count > 0

    def update_expense_category(self, expense_id: int, category: str) -> bool:
        """Update category for an expense (by local ID)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE expenses SET ai_category = ? WHERE id = ?
        ''', (category, expense_id))
        
        row_count = cursor.rowcount
        conn.commit()
        conn.close()
        return row_count > 0
