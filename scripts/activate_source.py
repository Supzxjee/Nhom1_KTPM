"""Upload -> verify -> activate one document against the locally running FastAPI server.

This helper is for a classroom project. With --demo, it activates a clearly labeled
synthetic test file, not an official HCMUE source. Without --demo, the user must
confirm that they manually verified the file against an official source.
"""
import argparse
import os
from pathlib import Path
import sys

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')


def request_or_exit(client, method, path, **kwargs):
    try:
        r = client.request(method, path, **kwargs)
    except httpx.HTTPError as e:
        raise SystemExit(f"Không kết nối được backend: {type(e).__name__}. Đã chạy uvicorn chưa?") from e
    if r.is_error:
        try:
            body = r.json()
            detail = body.get('error', body)
        except ValueError:
            detail = 'Server trả về phản hồi không hợp lệ.'
        raise SystemExit(f"{method} {path} thất bại (HTTP {r.status_code}): {detail}")
    return r.json()


def main():
    p=argparse.ArgumentParser(description='Nạp, xác nhận và kích hoạt tài liệu ở local server')
    p.add_argument('--file', required=True, help='Đường dẫn tới tài liệu PDF/TXT')
    p.add_argument('--source-id', required=True, help='Mã nguồn, ví dụ HCMUE-SPS-2026-01')
    p.add_argument('--url', default='http://127.0.0.1:8000')
    p.add_argument('--demo', action='store_true', help='Chỉ dùng cho nguồn mẫu TEST_ONLY; KHÔNG phải xác minh chính thức')
    args=p.parse_args()
    file=Path(args.file).expanduser()
    if not file.is_file(): p.error(f'Không tìm thấy tệp: {file}')
    if file.suffix.lower() not in ('.pdf','.txt'): p.error('Chỉ hỗ trợ PDF và TXT.')
    if file.stat().st_size > 10 * 1024 * 1024: p.error('Tệp vượt quá 10 MiB.')
    if args.demo:
        if 'TEST_ONLY' not in file.name.upper():
            p.error('--demo chỉ dành cho tệp chứa TEST_ONLY trong tên')
        print('CẢNH BÁO: Chỉ kích hoạt tài liệu thử nghiệm. Không được báo cáo là đã xác minh nguồn HCMUE.')
    else:
        if 'TEST_ONLY' in file.name.upper():
            p.error('Nguồn TEST_ONLY chỉ được kích hoạt với --demo.')
        print('Chỉ tiếp tục nếu bạn đã đối chiếu nội dung tài liệu với thông báo tuyển sinh chính thức.')
        if input('Gõ DA_DOI_CHIEU để xác nhận: ').strip() != 'DA_DOI_CHIEU':
            raise SystemExit('Đã hủy; chưa kích hoạt tài liệu.')
    token=os.getenv('ADMIN_TOKEN','').strip()
    if not token or token.startswith('REPLACE_'):
        raise SystemExit('Cần chỉnh ADMIN_TOKEN trong .env trước.')
    headers={'X-Admin-Token':token}
    # TEAM_USERNAME/TEAM_PASSWORD are optional for local use, required if cloud team access is enabled.
    team_user = os.getenv('TEAM_USERNAME', '').strip()
    team_password = os.getenv('TEAM_PASSWORD', '')
    if bool(team_user) != bool(team_password):
        raise SystemExit('TEAM_USERNAME và TEAM_PASSWORD phải cùng được cấu hình (hoặc cùng để trống).')
    auth = httpx.BasicAuth(team_user, team_password) if team_user else None
    with httpx.Client(base_url=args.url, timeout=90.0, trust_env=False, auth=auth) as c:
        with file.open('rb') as f:
            doc=request_or_exit(c, 'POST','/api/admin/documents', headers=headers,
                data={'source_id':args.source_id}, files={'file':(file.name,f)})
        version=doc['version_id']
        print('Đã tải:',version,'(draft)')
        request_or_exit(c, 'POST',f'/api/admin/documents/{version}/verify',
            headers=headers, json={'confirmed':True})
        print('Đã xác nhận theo lựa chọn của người chạy (verified).')
        active=request_or_exit(c, 'POST',f'/api/admin/documents/{version}/activate', headers=headers)
        print('Đã kích hoạt:',active['version_id'],'(active)')
        print(f'Chuyển sang {args.url}/ > Tạo phiên mới > Gửi câu hỏi.')
        print('Lưu ý: một thời điểm chỉ có 1 phiên bản tài liệu active; lần kích hoạt tiếp theo thay bản trước.')


if __name__=='__main__':
    main()
