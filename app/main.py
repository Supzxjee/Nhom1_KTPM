"""FastAPI starter aligned with HCMUE SRS v1.1 (11 contractual endpoints + 1 catalog UI endpoint)."""
import hmac
import base64
import binascii
import os
import httpx
import json
import logging
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, Form, Header, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict

from .config import get_settings
from .database import db_connect, initialize
from .llm import FALLBACK, answer
from .retrieval import expand_query_with_catalog, retrieve, text_from_upload
from .validators import validate_query

logger = logging.getLogger(__name__)
MAX_FILE_BYTES = 10 * 1024 * 1024

class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, field: str | None = None):
        self.status, self.code, self.message, self.field = status, code, message, field

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    session_id: str
    question: Any
    history_limit: Any = 5

class FavoriteRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    major_code: Any

class VerifyRequest(BaseModel):
    confirmed: bool = False


def require_valid(errors):
    if errors:
        e = errors[0]
        raise ApiError(422, e['code'], e['message'], e['field'])


def require_session(conn, session_id):
    if not conn.execute('SELECT 1 FROM sessions WHERE session_id=?', (session_id,)).fetchone():
        raise ApiError(404, 'SESSION_NOT_FOUND', 'Không tìm thấy phiên hội thoại.', 'session_id')


def require_admin(value, settings):
    if not settings.admin_token:
        raise ApiError(503, 'ADMIN_NOT_CONFIGURED', 'Máy chủ chưa cấu hình ADMIN_TOKEN.')
    if not value or not hmac.compare_digest(value, settings.admin_token):
        raise ApiError(401, 'UNAUTHORIZED', 'Thiếu hoặc sai X-Admin-Token.')


def create_app():
    settings = get_settings()
    team_user = os.getenv('TEAM_USERNAME', '').strip()
    team_password = os.getenv('TEAM_PASSWORD', '')
    if bool(team_user) != bool(team_password):
        raise RuntimeError('TEAM_USERNAME và TEAM_PASSWORD phải được cấu hình cùng nhau.')

    @asynccontextmanager
    async def lifespan(app):
        initialize(settings.db_path, settings.majors_csv)
        yield

    app = FastAPI(title='HCMUE Admissions Chatbot – SRS v1.1', version='0.7.0', lifespan=lifespan)
    app.state.settings = settings

    @app.middleware('http')
    async def team_login(request: Request, call_next):
        # /health must remain accessible for cloud health checks.
        if not team_user or request.url.path == '/health':
            return await call_next(request)
        supplied = request.headers.get('Authorization', '')
        valid = False
        if supplied.startswith('Basic '):
            try:
                raw = base64.b64decode(supplied[6:], validate=True).decode('utf-8')
                username, separator, password = raw.partition(':')
                valid = (bool(separator) and
                         hmac.compare_digest(username, team_user) and
                         hmac.compare_digest(password, team_password))
            except (ValueError, UnicodeDecodeError, binascii.Error):
                pass
        if not valid:
            return JSONResponse(
                status_code=401,
                content={'error': {'code': 'TEAM_LOGIN_REQUIRED',
                                   'message': 'Cần đăng nhập tài khoản nhóm kiểm thử.',
                                   'field': None}},
                headers={'WWW-Authenticate': 'Basic realm="HCMUE QA Team"',
                         'Cache-Control': 'no-store'})
        return await call_next(request)

    @app.exception_handler(ApiError)
    async def known_error(request: Request, exc: ApiError):
        return JSONResponse(status_code=exc.status,
                            content={'error': {'code': exc.code, 'message': exc.message, 'field': exc.field}})

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={
            'error': {'code': 'INVALID_REQUEST', 'message': 'Dữ liệu yêu cầu không đúng định dạng.',
                      'field': '.'.join(str(x) for x in exc.errors()[0]['loc'])}})

    @app.get('/', include_in_schema=False)
    def homepage():
        return FileResponse(Path(__file__).parent / 'index.html')

    @app.get('/health')
    def health():
        return {'ok': True, 'llm_mode': settings.llm_mode, 'llm_configured': (bool(settings.gemini_api_key) if settings.llm_mode == 'gemini' else (bool(settings.openai_api_key) if settings.llm_mode == 'openai' else (all((settings.llm_api_url, settings.llm_api_key, settings.llm_model)) if settings.llm_mode in ('compatible', 'api') else settings.llm_mode == 'mock'))), 'dataset': 'SPS_2026', 'dataset_verified': False}

    # Extension: browse complete source catalog, including alphanumeric official program codes.
    @app.get('/api/majors')
    def list_all_majors(year: str = Query('2026')):
        require_valid(validate_query(major_code='0000000', admission_year=int(year) if year.isdigit() else year))
        with db_connect(settings.db_path) as conn:
            rows = conn.execute('SELECT * FROM majors WHERE admission_year=? AND campus_code=? ORDER BY official_program_code',
                                (2026, 'SPS')).fetchall()
        return {'dataset_status': 'DRAFT_NOT_FULLY_VERIFIED', 'count': len(rows), 'items': [dict(r) for r in rows]}

    @app.get('/api/majors/{code}')
    def get_major(code: str, year: str = Query('2026')):
        require_valid(validate_query(major_code=code, admission_year=int(year) if year.isdigit() else year))
        with db_connect(settings.db_path) as conn:
            row = conn.execute('''SELECT * FROM majors WHERE official_program_code=?
                      AND major_code_7=? AND admission_year=? AND campus_code='SPS' ''',
                               (code, code, 2026)).fetchone()
        if not row:
            raise ApiError(404, 'MAJOR_NOT_FOUND', 'Không tìm thấy mã ngành trong danh mục đang hỗ trợ.', 'major_code')
        return dict(row)

    @app.post('/api/sessions', status_code=201)
    def create_session():
        sid = str(uuid4())
        with db_connect(settings.db_path) as conn:
            conn.execute('INSERT INTO sessions(session_id) VALUES (?)', (sid,))
        return {'session_id': sid}

    @app.get('/api/sessions/{session_id}/messages')
    def get_messages(session_id: str):
        with db_connect(settings.db_path) as conn:
            require_session(conn, session_id)
            rows = conn.execute('''SELECT message_id,role,content,citations_json,document_version_id,created_at
                                   FROM messages WHERE session_id=? ORDER BY created_at, rowid''', (session_id,)).fetchall()
        return {'session_id': session_id, 'messages': [{**dict(r), 'citations': json.loads(r['citations_json'])}
                for r in rows]}

    @app.delete('/api/sessions/{session_id}/messages', status_code=204)
    def delete_messages(session_id: str):
        with db_connect(settings.db_path) as conn:
            require_session(conn, session_id)
            conn.execute('DELETE FROM messages WHERE session_id=?', (session_id,))
        return Response(status_code=204)

    @app.get('/api/sessions/{session_id}/favorites')
    def get_favorites(session_id: str):
        with db_connect(settings.db_path) as conn:
            require_session(conn, session_id)
            rows = conn.execute('''SELECT f.major_code, m.major_name FROM favorites f
                JOIN majors m ON f.major_code=m.official_program_code AND m.admission_year=2026 AND m.campus_code='SPS'
                WHERE f.session_id=? ORDER BY f.created_at, f.rowid''', (session_id,)).fetchall()
        return {'session_id': session_id, 'items': [dict(r) for r in rows]}

    @app.post('/api/sessions/{session_id}/favorites')
    def add_favorite(session_id: str, item: FavoriteRequest):
        require_valid(validate_query(major_code=item.major_code))
        code = item.major_code
        with db_connect(settings.db_path) as conn:
            require_session(conn, session_id)
            exists = conn.execute('''SELECT 1 FROM majors WHERE official_program_code=? AND major_code_7=?
                                     AND admission_year=2026 AND campus_code='SPS' ''', (code, code)).fetchone()
            if not exists:
                raise ApiError(404, 'MAJOR_NOT_FOUND', 'Mã ngành không tồn tại trong danh mục.', 'major_code')
            if conn.execute('SELECT 1 FROM favorites WHERE session_id=? AND major_code=?', (session_id, code)).fetchone():
                raise ApiError(409, 'DUPLICATE_FAVORITE', 'Ngành đã được lưu.', 'major_code')
            count = conn.execute('SELECT COUNT(*) FROM favorites WHERE session_id=?', (session_id,)).fetchone()[0]
            if count >= 5:
                raise ApiError(409, 'FAVORITES_FULL', 'Chỉ được lưu tối đa 5 ngành.')
            conn.execute('INSERT INTO favorites(session_id,major_code) VALUES (?,?)', (session_id, code))
        return {'added': code, 'count': count+1}

    @app.delete('/api/sessions/{session_id}/favorites/{code}', status_code=204)
    def delete_favorite(session_id: str, code: str):
        require_valid(validate_query(major_code=code))
        with db_connect(settings.db_path) as conn:
            require_session(conn, session_id)
            cur = conn.execute('DELETE FROM favorites WHERE session_id=? AND major_code=?', (session_id, code))
            if cur.rowcount == 0:
                raise ApiError(404, 'FAVORITE_NOT_FOUND', 'Ngành chưa được lưu.', 'major_code')
        return Response(status_code=204)

    @app.post('/api/admin/documents', status_code=201)
    async def upload_document(file: UploadFile = File(...), source_id: str = Form(...),
                              x_admin_token: str | None = Header(default=None, alias='X-Admin-Token')):
        require_admin(x_admin_token, settings)
        name = Path(file.filename or '').name
        if not name.lower().endswith(('.pdf', '.txt')):
            raise ApiError(422, 'UNSUPPORTED_FILE_TYPE', 'Chỉ hỗ trợ .pdf hoặc .txt.', 'file')
        contents = await file.read(MAX_FILE_BYTES + 1)
        if len(contents) > MAX_FILE_BYTES:
            raise ApiError(422, 'FILE_TOO_LARGE', 'Tệp tối đa 10 MiB.', 'file')
        if not contents:
            raise ApiError(422, 'EMPTY_FILE', 'Tệp không được rỗng.', 'file')
        if name.lower().endswith('.pdf') and not contents.startswith(b'%PDF'):
            raise ApiError(422, 'INVALID_PDF', 'Tệp tải lên không đúng định dạng PDF.', 'file')
        try:
            text = text_from_upload(name, contents)
        except ValueError as exc:
            raise ApiError(422, 'INVALID_DOCUMENT', str(exc), 'file') from exc
        version_id = 'DV-' + uuid4().hex[:12].upper()
        with db_connect(settings.db_path) as conn:
            conn.execute('''INSERT INTO document_versions(version_id,dataset_id,source_id,filename,status,text_content)
                            VALUES (?,'SPS_2026',?,?,'draft',?)''', (version_id, source_id, name, text))
        return {'version_id': version_id, 'status': 'draft', 'source_id': source_id,
                'note': 'Chưa được xác minh bởi quản trị viên.'}

    @app.post('/api/admin/documents/{version_id}/verify')
    def verify_document(version_id: str, data: VerifyRequest,
                        x_admin_token: str | None = Header(default=None, alias='X-Admin-Token')):
        require_admin(x_admin_token, settings)
        if not data.confirmed:
            raise ApiError(422, 'CONFIRMATION_REQUIRED', 'Quản trị viên phải xác nhận đã đối chiếu nguồn.', 'confirmed')
        with db_connect(settings.db_path) as conn:
            row = conn.execute('SELECT status FROM document_versions WHERE version_id=?', (version_id,)).fetchone()
            if not row:
                raise ApiError(404, 'DOCUMENT_NOT_FOUND', 'Không thấy phiên bản tài liệu.')
            if row['status'] != 'draft':
                raise ApiError(409, 'INVALID_STATE', 'Chỉ chuyển từ Nháp sang Đã kiểm tra.')
            conn.execute('''UPDATE document_versions SET status='verified', verified_at=CURRENT_TIMESTAMP
                            WHERE version_id=?''', (version_id,))
        return {'version_id': version_id, 'status': 'verified',
                'note': 'Được quản trị viên xác nhận; hệ thống không tự xác thực độ đúng của nguồn.'}

    @app.post('/api/admin/documents/{version_id}/activate')
    def activate_document(version_id: str,
                          x_admin_token: str | None = Header(default=None, alias='X-Admin-Token')):
        require_admin(x_admin_token, settings)
        with db_connect(settings.db_path) as conn:
            conn.execute('BEGIN IMMEDIATE')
            row = conn.execute('SELECT status FROM document_versions WHERE version_id=?', (version_id,)).fetchone()
            if not row:
                raise ApiError(404, 'DOCUMENT_NOT_FOUND', 'Không thấy phiên bản tài liệu.')
            if row['status'] != 'verified':
                raise ApiError(409, 'INVALID_STATE', 'Chỉ kích hoạt phiên bản Đã kiểm tra.')
            conn.execute("UPDATE document_versions SET status='replaced' WHERE dataset_id='SPS_2026' AND status='active'")
            conn.execute("UPDATE document_versions SET status='active',activated_at=CURRENT_TIMESTAMP WHERE version_id=?", (version_id,))
        return {'version_id': version_id, 'status': 'active'}

    @app.post('/api/chat')
    def chat(data: ChatRequest):
        require_valid(validate_query(question=data.question, history_limit=data.history_limit))
        with db_connect(settings.db_path) as conn:
            require_session(conn, data.session_id)
            row = conn.execute("SELECT * FROM document_versions WHERE dataset_id='SPS_2026' AND status='active'").fetchone()
            if not row:
                raise ApiError(503, 'NO_ACTIVE_DOCUMENT', 'Chưa có tài liệu nguồn được kích hoạt.')
            if data.history_limit:
                old = conn.execute('''SELECT role,content FROM messages WHERE session_id=?
                                      ORDER BY rowid DESC LIMIT ?''', (data.session_id, data.history_limit)).fetchall()
                history = [dict(x) for x in reversed(old)]
            else:
                history = []
            # Load major catalog for query expansion (name → code boosting).
            catalog_rows = conn.execute(
                "SELECT major_name, major_code_7 FROM majors WHERE admission_year=2026 AND campus_code='SPS'"
            ).fetchall()
            catalog = [(r['major_name'], r['major_code_7']) for r in catalog_rows]
            expanded_q = expand_query_with_catalog(data.question.strip(), catalog)
            matches = retrieve(expanded_q, row['text_content'], catalog=catalog)
            citations = [{'source_id': row['source_id'], 'document_version_id': row['version_id'],
                          'section': m['section']} for m in matches]
            try:
                response = answer(data.question.strip(), matches, settings, history=history)
            except httpx.HTTPStatusError as exc:
                # Never log request headers, URLs containing keys, or provider response bodies.
                logger.warning('LLM provider returned HTTP %s', exc.response.status_code)
                raise ApiError(503, 'LLM_UNAVAILABLE',
                               f'Gemini API trả lỗi HTTP {exc.response.status_code}; kiểm tra key, model và hạn mức.'
                               if settings.llm_mode == 'gemini' else 'Dịch vụ mô hình AI tạm không sẵn sàng.') from exc
            except (httpx.HTTPError, RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
                logger.warning('LLM call failed (%s)', type(exc).__name__)
                raise ApiError(503, 'LLM_UNAVAILABLE', 'Dịch vụ mô hình AI tạm không sẵn sàng.') from exc
            # No source claim when text retrieval found nothing.
            if response == FALLBACK:
                citations = []
            conn.execute('''INSERT INTO messages(message_id,session_id,role,content,citations_json,document_version_id)
                            VALUES (?,?,?,?,?,?)''', (str(uuid4()), data.session_id, 'user', data.question.strip(), '[]', row['version_id']))
            conn.execute('''INSERT INTO messages(message_id,session_id,role,content,citations_json,document_version_id)
                            VALUES (?,?,?,?,?,?)''', (str(uuid4()), data.session_id, 'assistant', response,
                                                      json.dumps(citations, ensure_ascii=False), row['version_id']))
        return {'session_id': data.session_id, 'answer': response, 'citations': citations,
                'document_version_id': row['version_id'], 'mode': settings.llm_mode}

    return app

app = create_app()
