from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import DB_URL
from models import Base

engine = create_async_engine(DB_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)