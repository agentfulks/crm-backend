"""Test database connection script.

Usage:
    export DATABASE_URL="postgresql+psycopg://user:pass@host:port/db"
    python scripts/test_db_connection.py

Or with .env file:
    echo "DATABASE_URL=postgresql+psycopg://user:pass@host:port/db" > .env
    python scripts/test_db_connection.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.session import SessionLocal


def test_connection() -> bool:
    """Test database connectivity."""
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1"))
        result.fetchone()
        print("✅ Database connection OK")
        return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        session.close()


def test_tables_exist() -> bool:
    """Verify all expected tables exist."""
    from app.db.base import Base
    from app.db.base import import_models
    
    # Import all models to register them with Base
    import_models()
    
    expected_tables = set(Base.metadata.tables.keys())
    
    session = SessionLocal()
    try:
        result = session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        existing_tables = {row[0] for row in result}
        
        missing = expected_tables - existing_tables
        extra = existing_tables - expected_tables
        
        if missing:
            print(f"❌ Missing tables: {missing}")
            return False
        
        print(f"✅ All {len(expected_tables)} tables exist:")
        for table in sorted(expected_tables):
            print(f"   - {table}")
        
        if extra:
            print(f"ℹ️ Extra tables in database: {extra}")
        
        return True
    except OperationalError as e:
        print(f"❌ Failed to check tables: {e}")
        return False
    finally:
        session.close()


def main():
    """Run all connection tests."""
    print("=" * 60)
    print("VC Outreach CRM - Database Connection Test")
    print("=" * 60)
    print()
    
    # Test basic connectivity
    print("Testing database connectivity...")
    if not test_connection():
        print()
        print("❌ Connection test failed. Check your DATABASE_URL.")
        sys.exit(1)
    print()
    
    # Test tables exist
    print("Checking tables...")
    if not test_tables_exist():
        print()
        print("❌ Table verification failed. Run: alembic upgrade head")
        sys.exit(1)
    print()
    
    print("=" * 60)
    print("✅ All database tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
