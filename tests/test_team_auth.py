"""QA team login gate: protect public endpoints, leave /health reachable."""
from fastapi.testclient import TestClient
from app.main import create_app


def test_public_mode_remains_compatible(client):
    assert client.get('/').status_code == 200
    assert client.post('/api/sessions').status_code == 201


def test_team_login_gate(monkeypatch, tmp_path):
    monkeypatch.setenv('DB_PATH', str(tmp_path / 'auth.db'))
    monkeypatch.setenv('LLM_MODE', 'mock')
    monkeypatch.setenv('ADMIN_TOKEN', 'test-admin-token')
    monkeypatch.setenv('TEAM_USERNAME', 'nhom1')
    monkeypatch.setenv('TEAM_PASSWORD', 'secret-for-tests')
    with TestClient(create_app()) as client:
        assert client.get('/health').status_code == 200
        assert client.get('/').status_code == 401
        assert client.get('/docs').status_code == 401
        assert client.get('/api/majors').status_code == 401
        assert client.get('/api/majors', auth=('nhom1','wrong')).status_code == 401
        r = client.get('/', auth=('nhom1','secret-for-tests'))
        assert r.status_code == 200
        r = client.post('/api/sessions', auth=('nhom1','secret-for-tests'))
        assert r.status_code == 201


def test_partial_team_credentials_fail_closed(monkeypatch):
    monkeypatch.setenv('TEAM_USERNAME', 'nhom1')
    monkeypatch.delenv('TEAM_PASSWORD', raising=False)
    try:
        create_app()
    except RuntimeError as exc:
        assert 'TEAM_USERNAME' in str(exc)
    else:
        assert False, 'Misconfigured gate should refuse startup'
