import pytest

ADMIN = {'X-Admin-Token':'test-admin-token'}

def test_health_and_browser(client):
    assert client.get('/').status_code == 200
    assert client.get('/health').json()['llm_mode'] == 'mock'

def test_browse_all_official_program_codes(client):
    r = client.get('/api/majors')
    assert r.status_code == 200
    assert r.json()['count'] >= 40
    assert any(x['official_program_code'] == '7140202SN' for x in r.json()['items'])
    assert r.json()['dataset_status'] == 'DRAFT_NOT_FULLY_VERIFIED'


def test_major_lookup_valid_and_bad(client):
    r = client.get('/api/majors/7140209?year=2026')
    assert r.status_code == 200
    assert r.json()['major_name'] == 'Sư phạm Toán học'
    assert client.get('/api/majors/7140202SN').status_code == 422
    assert client.get('/api/majors/714020').status_code == 422
    assert client.get('/api/majors/1234567').status_code == 404
    assert client.get('/api/majors/7140209?year=2025').status_code == 422


def test_create_and_delete_history_keeps_session(client,session_id,activated_document):
    r=client.post('/api/chat',json={'session_id':session_id, 'question':'Sư phạm Toán học?', 'history_limit':0})
    assert r.status_code == 200
    assert client.get(f'/api/sessions/{session_id}/messages').json()['messages']
    assert client.delete(f'/api/sessions/{session_id}/messages').status_code == 204
    assert client.get(f'/api/sessions/{session_id}/messages').json()['messages'] == []
    assert client.get(f'/api/sessions/{session_id}/favorites').status_code == 200


def test_missing_session(client):
    assert client.get('/api/sessions/nonexistent/messages').status_code == 404
    assert client.post('/api/chat', json={'session_id':'bad', 'question':'Hello'}).status_code == 404


def test_favorite_rules(client,session_id):
    codes = ['7140201','7140202','7140203','7140204','7140205','7140206']
    for code in codes[:5]:
        assert client.post(f'/api/sessions/{session_id}/favorites', json={'major_code': code}).status_code == 200
    dup=client.post(f'/api/sessions/{session_id}/favorites', json={'major_code': codes[0]})
    assert dup.status_code == 409
    full=client.post(f'/api/sessions/{session_id}/favorites', json={'major_code': codes[5]})
    assert full.status_code == 409
    assert len(client.get(f'/api/sessions/{session_id}/favorites').json()['items'])==5
    assert client.delete(f'/api/sessions/{session_id}/favorites/{codes[0]}').status_code == 204
    assert client.post(f'/api/sessions/{session_id}/favorites', json={'major_code': codes[5]}).status_code == 200
    assert len(client.get(f'/api/sessions/{session_id}/favorites').json()['items'])==5


def test_favorite_invalid_does_not_mutate(client,session_id):
    path=f'/api/sessions/{session_id}/favorites'
    assert client.post(path,json={'major_code':'1234567'}).status_code==404
    assert client.post(path,json={'major_code':'7140202SN'}).status_code==422
    assert client.post(path,json={'major_code':7140209}).status_code==422
    assert client.get(path).json()['items']==[]


def test_chat_no_active_and_validation(client,session_id):
    path='/api/chat'
    assert client.post(path,json={'session_id':session_id,'question':'ok'}).status_code==503
    assert client.post(path,json={'session_id':session_id,'question':' '}).status_code==422
    assert client.post(path,json={'session_id':session_id,'question':'x'*501}).status_code==422
    assert client.post(path,json={'session_id':session_id,'question':'ok','history_limit':11}).status_code==422
    assert client.post(path,json={'session_id':session_id,'question':'ok','history_limit':-1}).status_code==422
    assert client.post(path,json={'session_id':session_id,'question':'ok','history_limit':True}).status_code==422


def test_admin_missing_wrong_token(client):
    payload=dict(files={'file':('x.txt',b'hello','text/plain')},data={'source_id':'S-1'})
    assert client.post('/api/admin/documents',**payload).status_code==401
    assert client.post('/api/admin/documents',headers={'X-Admin-Token':'wrong'},**payload).status_code==401


def test_upload_invalid_formats(client):
    def upload(name,contents):
        return client.post('/api/admin/documents', headers=ADMIN,
                           files={'file':(name,contents)},data={'source_id':'TEST'})
    assert upload('data.json',b'{"x":1}').status_code==422
    assert upload('a.pdf',b'not a pdf').status_code==422
    assert upload('a.txt',b'').status_code==422
    assert upload('a.txt',b'a'*(10*1024*1024+1)).status_code==422
    assert upload('a.txt',b'\xff').status_code==422


def test_doc_states_and_chat_citations(client,session_id):
    r=client.post('/api/admin/documents',headers=ADMIN,files={'file':('hcmue.txt','Ngành Sư phạm Toán học mã 7140209.'.encode())},data={'source_id':'SRC-TEST'})
    assert r.status_code==201
    vid = r.json()['version_id']
    assert client.post(f'/api/admin/documents/{vid}/activate',headers=ADMIN).status_code==409
    assert client.post(f'/api/admin/documents/{vid}/verify',headers=ADMIN,json={'confirmed':False}).status_code==422
    assert client.post(f'/api/admin/documents/{vid}/verify',headers=ADMIN,json={'confirmed':True}).status_code==200
    assert client.post(f'/api/admin/documents/{vid}/verify',headers=ADMIN,json={'confirmed':True}).status_code==409
    assert client.post(f'/api/admin/documents/{vid}/activate',headers=ADMIN).status_code==200
    assert client.post(f'/api/admin/documents/{vid}/activate',headers=ADMIN).status_code==409
    chat=client.post('/api/chat',json={'session_id':session_id,'question':'Sư phạm Toán học là ngành gì?'}).json()
    assert chat['citations'][0]['source_id']=='SRC-TEST'
    assert chat['citations'][0]['document_version_id']==vid
    assert chat['mode']=='mock'
    unknown=client.post('/api/chat',json={'session_id':session_id,'question':'Zyzzyx foobar quux?'}).json()
    assert unknown['citations']==[]
    assert 'Chưa tìm thấy' in unknown['answer']


def test_switch_document_version(client,activated_document,session_id):
    r=client.post('/api/admin/documents',headers=ADMIN,
         files={'file':('new.txt',b'HCMUE SPS information second version.')},data={'source_id':'SRC-2'})
    vid=r.json()['version_id']
    assert client.post(f'/api/admin/documents/{vid}/verify',headers=ADMIN,json={'confirmed':True}).status_code==200
    assert client.post(f'/api/admin/documents/{vid}/activate',headers=ADMIN).status_code==200
    # Old version is now replaced; can no longer activate.
    assert client.post(f'/api/admin/documents/{activated_document}/activate',headers=ADMIN).status_code==409
    result=client.post('/api/chat',json={'session_id':session_id,'question':'second version'}).json()
    assert result['document_version_id']==vid


def test_error_envelope(client):
    r=client.get('/api/majors/abcd')
    assert r.status_code==422
    assert set(r.json()['error'])=={'code','message','field'}
