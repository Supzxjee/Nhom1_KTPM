"""Gemini integration tests use fake HTTP responses only: no network calls, no fees."""
from dataclasses import replace

import httpx
import pytest
from fastapi.testclient import TestClient

from app import llm
from app.config import get_settings
from app.main import create_app

SEGMENTS = [{'section':'Đoạn 1', 'excerpt':'Ngành Sư phạm Toán học có mã ngành 7140209.'}]

def settings():
    return replace(get_settings(), llm_mode='gemini', gemini_api_key='fake-unit-test-only', gemini_model='gemini-3.5-flash-lite')

def fake_success(url, *, headers, json, timeout):
    return httpx.Response(200, json={'candidates':[{'content':{'role':'model','parts':[{'text':'Sư phạm Toán học có mã ngành 7140209 [Đoạn 1].'}]}}]}, request=httpx.Request('POST',url))

def test_gemini_payload_history_and_answer(monkeypatch):
    captured={}
    def fake_post(url, *, headers, json, timeout):
        captured.update(url=url, headers=headers, body=json, timeout=timeout)
        return fake_success(url,headers=headers,json=json,timeout=timeout)
    monkeypatch.setattr(llm.httpx,'post',fake_post)
    result=llm.answer('Mã ngành Sư phạm Toán?',SEGMENTS,settings(),history=[{'role':'user','content':'Xin chào'}, {'role':'assistant','content':'Chào bạn'}])
    assert '7140209' in result
    assert captured['url'].endswith('/models/gemini-3.5-flash-lite:generateContent')
    assert captured['headers']['x-goog-api-key']=='fake-unit-test-only'
    assert 'systemInstruction' in captured['body']
    assert [c['role'] for c in captured['body']['contents']]==['user','model','user']
    assert 'Đoạn 1' in captured['body']['contents'][-1]['parts'][0]['text']
    assert captured['body']['generationConfig']['temperature']==0.1

def test_gemini_no_source_does_not_call_network(monkeypatch):
    monkeypatch.setattr(llm.httpx,'post',lambda *a,**kw: (_ for _ in ()).throw(AssertionError('Unexpected network')))
    assert llm.answer('Unknown?',[],settings())==llm.FALLBACK

def test_gemini_missing_key_no_network(monkeypatch):
    monkeypatch.setattr(llm.httpx,'post',lambda *a,**kw: (_ for _ in ()).throw(AssertionError('Unexpected network')))
    with pytest.raises(RuntimeError, match='GEMINI_API_KEY'):
        llm.answer('Sư phạm Toán học?',SEGMENTS,replace(settings(),gemini_api_key=''))

def test_gemini_empty_response_error(monkeypatch):
    monkeypatch.setattr(llm.httpx,'post',lambda url,**kw: httpx.Response(200,json={'candidates':[{'finishReason':'SAFETY'}]},request=httpx.Request('POST',url)))
    with pytest.raises(RuntimeError,match='Gemini không trả về văn bản'):
        llm.answer('Sư phạm Toán?',SEGMENTS,settings())

def test_gemini_401_is_http_status_error(monkeypatch):
    monkeypatch.setattr(llm.httpx,'post',lambda url,**kw: httpx.Response(401,json={'error':{'message':'Key invalid'}},request=httpx.Request('POST',url)))
    with pytest.raises(httpx.HTTPStatusError):
        llm.answer('Sư phạm Toán?',SEGMENTS,settings())

def test_server_gemini_path_end_to_end_offline(tmp_path,monkeypatch):
    monkeypatch.setenv('DB_PATH',str(tmp_path/'gemini-test.db'))
    monkeypatch.setenv('ADMIN_TOKEN','admin-test-only')
    monkeypatch.setenv('LLM_MODE','gemini')
    monkeypatch.setenv('GEMINI_API_KEY','fake-gemini-key')
    monkeypatch.setenv('GEMINI_MODEL','gemini-3.5-flash-lite')
    count=[]
    def fake_post(url,**kw):
        count.append(url)
        return fake_success(url,**kw)
    monkeypatch.setattr(llm.httpx,'post',fake_post)
    with TestClient(create_app()) as c:
        health=c.get('/health').json()
        assert health['llm_mode']=='gemini' and health['llm_configured'] is True
        sid=c.post('/api/sessions').json()['session_id']
        upload=c.post('/api/admin/documents',headers={'X-Admin-Token':'admin-test-only'},files={'file':('data.txt',b'Su pham Toan hoc: 7140209')},data={'source_id':'TEST'})
        assert upload.status_code==201
        ver=upload.json()['version_id']
        assert c.post(f'/api/admin/documents/{ver}/verify',headers={'X-Admin-Token':'admin-test-only'},json={'confirmed':True}).status_code==200
        assert c.post(f'/api/admin/documents/{ver}/activate',headers={'X-Admin-Token':'admin-test-only'}).status_code==200
        chat=c.post('/api/chat',json={'session_id':sid,'question':'Su pham Toan hoc?'})
        assert chat.status_code==200,chat.text
        assert chat.json()['mode']=='gemini'
        assert '7140209' in chat.json()['answer']
        assert len(count)==1
        history=c.get(f'/api/sessions/{sid}/messages').json()['messages']
        assert len(history)==2

def test_server_gemini_http_error_sanitized(tmp_path,monkeypatch):
    monkeypatch.setenv('DB_PATH',str(tmp_path/'gemini-error.db'))
    monkeypatch.setenv('ADMIN_TOKEN','admin-test-only')
    monkeypatch.setenv('LLM_MODE','gemini')
    monkeypatch.setenv('GEMINI_API_KEY','fake-secret-must-never-leak')
    monkeypatch.setenv('GEMINI_MODEL','gemini-3.5-flash-lite')
    def fake_post(url,**kw):
        return httpx.Response(429,json={'error':{'message':'Please retry; secret fake-secret-must-never-leak'}},request=httpx.Request('POST',url))
    monkeypatch.setattr(llm.httpx,'post',fake_post)
    with TestClient(create_app()) as c:
        sid=c.post('/api/sessions').json()['session_id']
        up=c.post('/api/admin/documents',headers={'X-Admin-Token':'admin-test-only'},files={'file':('data.txt',b'Su pham Toan hoc: 7140209')},data={'source_id':'TEST'})
        ver=up.json()['version_id']
        c.post(f'/api/admin/documents/{ver}/verify',headers={'X-Admin-Token':'admin-test-only'},json={'confirmed':True})
        c.post(f'/api/admin/documents/{ver}/activate',headers={'X-Admin-Token':'admin-test-only'})
        r=c.post('/api/chat',json={'session_id':sid,'question':'Su pham Toan hoc?'})
        assert r.status_code==503
        assert 'HTTP 429' in r.text
        assert 'fake-secret' not in r.text
        assert not c.get(f'/api/sessions/{sid}/messages').json()['messages']
