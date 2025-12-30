"""Database connection and session management."""

from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from loguru import logger

from src.config.settings import settings
from src.database.models import Base


class Database:
    """Database manager."""
    
    def __init__(self):
        """Initialize database connection."""
        db_path = Path(settings.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create async engine
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )
        
        # Create session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        logger.info(f"Database initialized at {db_path}")
    
    async def create_tables(self):
        """Create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    
    async def drop_tables(self):
        """Drop all tables (use with caution)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("Database tables dropped")
    
    async def close(self):
        """Close database connection."""
        await self.engine.dispose()
        logger.info("Database connection closed")
    
    def get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.async_session()


# Global database instance
db = Database()


async def init_database():
    """Initialize database and create tables."""
    await db.create_tables()


if __name__ == "__main__":
    """Run this script to initialize the database."""
    import asyncio
    
    async def main():
        logger.info("Initializing database...")
        await init_database()
        logger.success("Database initialized successfully!")
        await db.close()
    
    asyncio.run(main())
