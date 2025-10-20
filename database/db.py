"""
Database configuration and connection management.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import asyncio
import ssl as ssl_module

from config import settings

# Convert database URL for async  driver
# Remove sslmode from query string and handle it via connect_args
def prepare_database_url(url: str, async_driver: bool = False) -> tuple:
    """Prepare database URL and connect args for SQLAlchemy."""
    # Remove sslmode parameter
    url_clean = url.replace('?sslmode=require', '').replace('&sslmode=require', '')
    
    if async_driver:
        url_clean = url_clean.replace("postgres://", "postgresql+asyncpg://")
    else:
        url_clean = url_clean.replace("postgres://", "postgresql://")
    
    # Prepare SSL context for asyncpg
    connect_args = {}
    if 'sslmode=require' in url:
        ssl_context = ssl_module.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl_module.CERT_NONE
        connect_args = {"ssl": ssl_context}
    
    return url_clean, connect_args

# Prepare URLs
DATABASE_URL, _ = prepare_database_url(settings.database_url, async_driver=False)
ASYNC_DATABASE_URL, async_connect_args = prepare_database_url(settings.database_url, async_driver=True)

# Create sync engine for initial setup
sync_engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Create async engine for application use
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args=async_connect_args,
    poolclass=NullPool,
    echo=settings.debug
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db():
    """
    Dependency to get database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database: create tables and enable pgvector extension.
    """
    try:
        # Import models to register them
        from database import models
        
        # Create tables using async engine
        async with async_engine.begin() as conn:
            # Enable pgvector extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise


async def close_db():
    """
    Close database connections.
    """
    await async_engine.dispose()
