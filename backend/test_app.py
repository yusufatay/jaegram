import pytest
from fastapi.testclient import TestClient
from app import app
from backend.models import Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_client():
    # Test veritabanı oluştur
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

def test_register_and_login(test_client):
    r = test_client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert r.status_code == 200
    r = test_client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

def test_take_task_flow(test_client):
    # Önce kullanıcı oluştur ve login ol
    test_client.post("/register", json={"username": "taskuser", "password": "1234"})
    r = test_client.post("/login", data={"username": "taskuser", "password": "1234"})
    token = r.json()["access_token"]
    # Sipariş oluştur (admin yetkisi gerekmez)
    order = {"post_url": "https://instagram.com/p/test", "order_type": "like", "target_count": 1}
    test_client.post("/create-order", json=order, headers={"Authorization": f"Bearer {token}"})
    # Görev al
    r = test_client.post("/take-task", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    # Görev tamamla
    task_id = r.json()["task_id"]
    r = test_client.post("/complete-task", json={"task_id": task_id}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

def test_admin_ban_and_push(test_client):
    # Admin kullanıcı oluştur
    test_client.post("/register", json={"username": "admin", "password": "adminpass", "full_name": "Admin"})
    # Admin login
    r = test_client.post("/login", data={"username": "admin", "password": "adminpass"})
    token = r.json()["access_token"]
    # Admin yetkisi ver (manuel DB update gerekebilir)
    # Burada doğrudan DB update yapılabilir veya test için User modeline erişilebilir
    # Ban endpointi ve push notification endpointi test edilebilir
    # ... 