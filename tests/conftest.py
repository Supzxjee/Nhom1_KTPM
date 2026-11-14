import os
import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture(autouse=True)
def _clear_team_auth_env():
    """Disable team-login gate and auto-seed for ALL tests unless explicitly set.

    The .env file at repo root loads TEAM_USERNAME/TEAM_PASSWORD into
    os.environ at import time (via load_dotenv).  monkeypatch.delenv() arrives
    too late for fixtures that call create_app() before monkeypatch is applied.
    We therefore save/restore os.environ directly so the gate is always off
    unless a test explicitly re-enables it.

    AUTO_SEED is also disabled so tests that expect an empty DB (e.g.
    test_chat_no_active_and_validation) are not affected by startup seeding.
    """
    keys_to_clear = ('TEAM_USERNAME', 'TEAM_PASSWORD')
    saved = {k: os.environ.pop(k) for k in keys_to_clear if k in os.environ}
    # Disable auto-seed; tests that need a document upload their own fixture.
    old_seed = os.environ.get('AUTO_SEED')
    os.environ['AUTO_SEED'] = '0'
    yield
    os.environ.update(saved)
    if old_seed is None:
        os.environ.pop('AUTO_SEED', None)
    else:
        os.environ['AUTO_SEED'] = old_seed


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DB_PATH', str(tmp_path / 'test.db'))
    monkeypatch.setenv('LLM_MODE', 'mock')
    monkeypatch.setenv('ADMIN_TOKEN', 'test-admin-token')
    monkeypatch.setenv('AUTO_SEED', '0')   # start with empty DB; tests seed their own docs
    with TestClient(create_app()) as client:
        yield client


@pytest.fixture
def session_id(client):
    result = client.post('/api/sessions')
    assert result.status_code == 201
    return result.json()['session_id']


@pytest.fixture
def activated_document(client):
    upload = client.post('/api/admin/documents', headers={'X-Admin-Token': 'test-admin-token'},
           files={'file': ('test_source.txt', 'Ngành Sư phạm Toán học mã 7140209.\n\nNgành Giáo dục Tiểu học mã 7140202.'.encode('utf-8'), 'text/plain')},
           data={'source_id': 'SRC-TEST-01'})
    assert upload.status_code == 201, upload.text
    ver = upload.json()['version_id']
    res = client.post(f'/api/admin/documents/{ver}/verify', headers={'X-Admin-Token': 'test-admin-token'}, json={'confirmed': True})
    assert res.status_code == 200, res.text
    res = client.post(f'/api/admin/documents/{ver}/activate', headers={'X-Admin-Token': 'test-admin-token'})
    assert res.status_code == 200, res.text
    return ver

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
