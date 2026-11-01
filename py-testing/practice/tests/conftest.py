import httpx
import pytest
import pytest_asyncio

from study_app.api import create_app
from study_app.storage import Notes


@pytest.fixture
def notes(tmp_path):
    storage = Notes(tmp_path / "notes.db")
    try:
        yield storage
    finally:
        storage.close()


@pytest_asyncio.fixture
async def api_client():
    # В этом приложении нет lifespan-ресурсов; ASGITransport сам lifespan не запускает.
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
