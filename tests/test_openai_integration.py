"""Offline tests that mock HTTP responses; no user API key or live billing needed."""
from dataclasses import replace
import httpx
import pytest
from fastapi.testclient import TestClient
from app import llm
from app.config import get_settings
from app.main import create_app

SEGMENTS = [{'section': 'Đoạn 1', 'excerpt': 'Ngành Sư phạm Toán học có mã ngành 7140209.'}]


def _settings():
    return replace(get_settings(), llm_mode='openai', openai_api_key='sk-fake-unit-test', openai_model='gpt-6-luna')


def test_real_api_payload_and_answer_parsing(monkeypatch):
    captured = {}
    def fake_post(url, *, headers, json, timeout):
        captured.update(url=url, headers=headers, json=json, timeout=timeout)
        return httpx.Response(200, json={'output': [
            {'type': 'message', 'role': 'assistant', 'content': [
                {'type': 'output_text', 'text': 'Sư phạm Toán học có mã 7140209 [Đoạn 1].'}
            ]}
        ]}, request=httpx.Request('POST', url))
    monkeypatch.setattr(llm.httpx, 'post', fake_post)
    result = llm.answer('Mã ngành Sư phạm Toán học?', SEGMENTS, _settings(),
                        history=[{'role':'user','content':'Xin chào'}])
    assert '7140209' in result
    assert captured['url'] == 'https://api.openai.com/v1/responses'
    assert captured['headers']['Authorization'] == 'Bearer sk-fake-unit-test'
    assert captured['json']['model'] == 'gpt-6-luna'
    assert captured['json']['store'] is False
    assert captured['json']['input'][-1]['role'] == 'user'
    assert 'Đoạn 1' in captured['json']['input'][-1]['content']
    assert captured['json']['input'][0]['content'] == 'Xin chào'


def test_no_retrieval_does_not_contact_openai(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Không được gọi API khi không tìm được trích đoạn.')
    monkeypatch.setattr(llm.httpx, 'post', deny)
    assert llm.answer('Không có tài liệu?', [], _settings()) == llm.FALLBACK


def test_api_key_missing_is_rejected_without_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Không được gọi API khi thiếu khóa.')
    monkeypatch.setattr(llm.httpx, 'post', deny)
    with pytest.raises(RuntimeError, match='OPENAI_API_KEY'):
        llm.answer('Sư phạm Toán?', SEGMENTS, replace(_settings(), openai_api_key=''))


def test_openai_unauthorized_http_error(monkeypatch):
    def fake_post(url, **kwargs):
        return httpx.Response(401, json={'error': {'message': 'Invalid API key'}},
                              request=httpx.Request('POST', url))
    monkeypatch.setattr(llm.httpx, 'post', fake_post)
    with pytest.raises(httpx.HTTPStatusError):
        llm.answer('Sư phạm Toán?', SEGMENTS, _settings())


def test_server_openai_live_path_mock_http(tmp_path, monkeypatch):
    """Exercise POST /api/chat -> RAG -> HTTP Responses parser end-to-end, offline."""
    monkeypatch.setenv('DB_PATH', str(tmp_path / 'real-path.db'))
    monkeypatch.setenv('ADMIN_TOKEN', 'test-secret')
    monkeypatch.setenv('LLM_MODE', 'openai')
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-fake-unit-test')
    monkeypatch.setenv('OPENAI_MODEL', 'gpt-6-luna')
    calls = []
    def fake_post(url, **kwargs):
        calls.append(url)
        return httpx.Response(200, json={'output': [
            {'type':'message','role':'assistant','content':[
                {'type':'output_text','text':'Mã ngành là 7140209 [Đoạn 1].'}
            ]}
        ]}, request=httpx.Request('POST',url))
    monkeypatch.setattr(llm.httpx, 'post', fake_post)
    with TestClient(create_app()) as c:
        assert c.get('/health').json()['llm_configured'] is True
        session = c.post('/api/sessions').json()['session_id']
        upload = c.post('/api/admin/documents',headers={'X-Admin-Token':'test-secret'},
                        files={'file':('source.txt','Ngành Sư phạm Toán học có mã ngành 7140209.'.encode('utf-8'))},
                        data={'source_id':'SRC-UNIT-TEST'})
        assert upload.status_code == 201, upload.text
        version = upload.json()['version_id']
        assert c.post(f'/api/admin/documents/{version}/verify',headers={'X-Admin-Token':'test-secret'},json={'confirmed':True}).status_code == 200
        assert c.post(f'/api/admin/documents/{version}/activate',headers={'X-Admin-Token':'test-secret'}).status_code == 200
        chat = c.post('/api/chat',json={'session_id':session, 'question':'Ngành Sư phạm Toán học mã bao nhiêu?'})
        assert chat.status_code == 200, chat.text
        assert chat.json()['mode'] == 'openai'
        assert '7140209' in chat.json()['answer']
        assert chat.json()['citations'][0]['source_id'] == 'SRC-UNIT-TEST'
        assert calls == ['https://api.openai.com/v1/responses']
        # SQL conversation persistence is still operational.
        assert len(c.get(f'/api/sessions/{session}/messages').json()['messages']) == 2


def test_failed_live_call_does_not_expose_key_or_persist(tmp_path, monkeypatch):
    monkeypatch.setenv('DB_PATH', str(tmp_path / 'failed.db'))
    monkeypatch.setenv('ADMIN_TOKEN', 'test-secret')
    monkeypatch.setenv('LLM_MODE', 'openai')
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-fake-secret-should-not-leak')
    def fake_post(url, **kwargs):
        return httpx.Response(429, json={'error':{'message':'Too many requests'}},
                              request=httpx.Request('POST', url))
    monkeypatch.setattr(llm.httpx, 'post', fake_post)
    with TestClient(create_app()) as c:
        session = c.post('/api/sessions').json()['session_id']
        upload = c.post('/api/admin/documents',headers={'X-Admin-Token':'test-secret'},
                        files={'file':('source.txt', 'Sư phạm Toán học mã 7140209.'.encode('utf-8'))},
                        data={'source_id':'SRC-TEST'})
        version = upload.json()['version_id']
        c.post(f'/api/admin/documents/{version}/verify',headers={'X-Admin-Token':'test-secret'},json={'confirmed':True})
        c.post(f'/api/admin/documents/{version}/activate',headers={'X-Admin-Token':'test-secret'})
        result=c.post('/api/chat',json={'session_id':session,'question':'Sư phạm Toán học?'})
        assert result.status_code == 503
        assert 'LLM_UNAVAILABLE' in result.text
        assert 'sk-fake-secret' not in result.text
        assert not c.get(f'/api/sessions/{session}/messages').json()['messages']
