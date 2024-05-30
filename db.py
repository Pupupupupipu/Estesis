import os

import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

url = f"postgresql+asyncpg://{os.environ.get('POSTGRES_USER')}:" \
      f"{os.environ.get('POSTGRES_PASSWORD')}" \
      f"@{os.environ.get('POSTGRES_HOST')}:" \
      f"{os.environ.get('POSTGRES_PORT')}" \
      f"/{os.environ.get('POSTGRES_DB')}"

engine = create_async_engine(url, echo=True)

sessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        pass
        # await conn.run_sync(Base.metadata.create_all())
        # await conn.run_sync(Base.metadata.drop_all())


async def get_session():
    async with sessionLocal() as session:
        yield session
