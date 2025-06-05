import pytest
from backend.app import app

def test_login():
    tester = app.test_client()
    response = tester.post('/api/login', json={'username': 'test', 'password': 'test'})
    assert response.status_code == 200

def test_get_tasks():
    tester = app.test_client()
    response = tester.get('/api/tasks')
    assert response.status_code == 200
