import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Load env test SEBELUM import app
load_dotenv(".env.test")

from databasebackend import get_db, init_db
from mainbackend import app
from auth import router as auth_router

app.include_router(auth_router)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Bikin tabel users sekali di awal testing."""
    init_db()
    yield
    # Cleanup setelah semua test selesai
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        cur.close()


@pytest.fixture
def client():
    """FastAPI TestClient — kirim request tanpa server."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_users_table():
    """Bersihin tabel users sebelum tiap test."""
    yield
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users")
        cur.close()