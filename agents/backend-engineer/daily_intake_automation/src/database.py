"""Database connection and queries for CRM."""

from contextlib import contextmanager
from typing import Generator, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from src.config import get_settings
from src.models import InvestorEntry


class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass


class CRMRepository:
    """Repository for CRM database operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize with database connection string."""
        self.database_url = database_url or get_settings().database_url
    
    @contextmanager
    def _get_connection(self) -> Generator:
        """Context manager for database connections."""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}") from e
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def _get_cursor(self, conn) -> Generator:
        """Context manager for database cursors."""
        cursor = None
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            yield cursor
        finally:
            if cursor:
                cursor.close()
    
    def get_top_scored_investors(self, limit: int = 5) -> List[InvestorEntry]:
        """
        Fetch top-scored investor entries from CRM.
        
        Args:
            limit: Maximum number of entries to fetch (default 5)
            
        Returns:
            List of InvestorEntry objects sorted by outreach_score descending
            
        Raises:
            DatabaseError: If database query fails
        """
        query = """
            SELECT 
                id,
                investor_name,
                firm_name,
                COALESCE(job_title, '') as job_title,
                email_address,
                phone_number,
                linkedin_profile_url,
                investment_thesis_summary,
                outreach_score,
                created_at,
                updated_at
            FROM investor_entries
            WHERE email_address IS NOT NULL
              AND email_address != ''
              AND investor_name IS NOT NULL
              AND investor_name != ''
              AND firm_name IS NOT NULL
              AND firm_name != ''
            ORDER BY outreach_score DESC, created_at DESC
            LIMIT %s
        """
        
        try:
            with self._get_connection() as conn:
                with self._get_cursor(conn) as cursor:
                    cursor.execute(query, (limit,))
                    rows = cursor.fetchall()
                    
                    entries = []
                    for row in rows:
                        try:
                            entry = InvestorEntry.model_validate(dict(row))
                            entries.append(entry)
                        except Exception as e:
                            # Log but continue - don't let one bad record stop the batch
                            print(f"Warning: Failed to parse investor entry {row.get('id')}: {e}")
                    
                    return entries
                    
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to fetch investor entries: {e}") from e
    
    def check_duplicate_card_exists(
        self, 
        investor_name: str, 
        lookback_days: int = 30
    ) -> bool:
        """
        Check if a card for this investor was already created recently.
        
        This is used as a secondary check in addition to the Trello API duplicate check.
        
        Args:
            investor_name: Name of the investor
            lookback_days: How far back to look for existing cards
            
        Returns:
            True if a duplicate exists, False otherwise
        """
        # This would check a local tracking table if implemented
        # For now, we rely on Trello's card name matching for duplicates
        return False
