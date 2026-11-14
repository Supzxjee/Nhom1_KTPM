import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DB_PATH', str(tmp_path / 'test.db'))
    monkeypatch.setenv('LLM_MODE', 'mock')
    monkeypatch.setenv('ADMIN_TOKEN', 'test-admin-token')
    with TestClient(create_app()) as client:
        yield client

@pytest.fixture
def session_id(client):
    result = client.post('/api/sessions')
    assert result.status_code == 201
    return result.json()['session_id']

@pytest.fixture
def activated_document(client):
    upload = client.post('/api/admin/documents', headers={'X-Admin-Token':'test-admin-token'},
           files={'file':('test_source.txt', 'Ngành Sư phạm Toán học mã 7140209.\n\nNgành Giáo dục Tiểu học mã 7140202.'.encode('utf-8'),'text/plain')},
           data={'source_id':'SRC-TEST-01'})
    assert upload.status_code == 201, upload.text
    ver = upload.json()['version_id']
    res = client.post(f'/api/admin/documents/{ver}/verify', headers={'X-Admin-Token':'test-admin-token'}, json={'confirmed':True})
    assert res.status_code == 200, res.text
    res = client.post(f'/api/admin/documents/{ver}/activate', headers={'X-Admin-Token':'test-admin-token'})
    assert res.status_code == 200, res.text
    return ver
