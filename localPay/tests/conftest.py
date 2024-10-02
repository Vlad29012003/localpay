import warnings
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

import sys
from dotenv import load_dotenv
import os

load_dotenv()


TEST_DB_NAME = os.getenv("TEST_DB_NAME")
TEST_DB_USER = os.getenv("TEST_DB_USER")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD")
TEST_DB_PORT = os.getenv("TEST_DB_PORT")
TEST_DB_IP = os.getenv("TEST_DB_IP")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from main import app


from db.database import get_db

from models.comment import Comment
from models.payment import Payment
from models.refresh_token import RefreshToken
from models.user import User

DATABASE_URL = os.getenv("TEST_DATABASE_URL",
                         f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_IP}:{TEST_DB_PORT}/{TEST_DB_NAME}")


engine_test = create_async_engine(DATABASE_URL , poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_db] = override_get_session



@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
