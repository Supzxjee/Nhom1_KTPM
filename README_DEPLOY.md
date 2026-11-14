# HCMUE Chatbot Gemini – v0.5 (triển khai cho nhóm kiểm thử)

**Mục đích:** đưa chatbot FastAPI + Gemini API + SQLite của nhóm lên Railway cho 4 thành viên cùng truy cập web. Đây là **dự án môn học**, không phải kênh tư vấn chính thức của HCMUE. Dữ liệu CSV ngành SPS 2026 là bản **dự thảo**; tài liệu PDF tuyển sinh chính thức trên **máy của bạn KHÔNG được đóng gói sẵn**, cần nạp lại lên web.

## Các khác biệt với v0.4
- Có `start_server.py`: lắng nghe `0.0.0.0` và biến môi trường `PORT` do Railway cấp.
- Dùng `DB_PATH=/data/chatbot.db` khi có volume `/data` để **lưu bền vững** phiên, lịch sử, ngành quan tâm và nội dung tài liệu đã nạp.
- Thêm bảo vệ **mật khẩu chung của nhóm** bằng HTTP Basic Auth (`TEAM_USERNAME`, `TEAM_PASSWORD`), không buộc người khác phải biết Gemini API key hoặc ADMIN_TOKEN. Để trống cả hai khi chạy local không cần đăng nhập.
- Script `scripts/activate_source.py` hỗ trợ `--url https://...` và tài khoản nhóm từ `.env` cục bộ.

## 1. Đưa code lên GitHub
1. Giải nén ZIP; mở đúng thư mục chứa `start_server.py`, `requirements.txt`, `app/` bằng VS Code.
2. Tạo repo mới, **nên để Private**, hoặc đưa các file **bên trong thư mục này** lên repo đã có của nhóm. Không push ZIP, `.env`, thư mục `.venv` hoặc tệp `chatbot.db`.
3. Với repo mới, từ thư mục dự án:

```powershell
git init
git add .
git commit -m "HCMUE chatbot Gemini deploy v0.5"
git branch -M main
git remote add origin https://github.com/TAI_KHOAN/TEN_REPO.git
git push -u origin main
```

Nếu repo đã có mã nguồn, hãy dùng quy trình commit/push hiện tại, đừng tự chạy `git init` hoặc thêm `origin` lần hai.

## 2. Railway: tạo Web Service
1. Truy cập https://railway.com/ -> New Project -> Deploy from GitHub repo -> chọn repo -> Deploy.
2. Chọn Web Service -> Settings -> **Start Command**: `python start_server.py`. Build Command nếu cần: `pip install -r requirements.txt`.
3. **Variables** (không push `.env`):

| Key | Value |
|---|---|
| `LLM_MODE` | `gemini` |
| `GEMINI_API_KEY` | API key Gemini thật của chủ dự án |
| `GEMINI_MODEL` | Model đã thử chạy thành công ở local (đang là `gemini-3.5-flash-lite` nếu tài khoản hỗ trợ) |
| `ADMIN_TOKEN` | Chuỗi ngẫu nhiên dài, chỉ quản trị viên biết |
| `TEAM_USERNAME` | `nhom1` (ví dụ) |
| `TEAM_PASSWORD` | Mật khẩu mạnh, nhóm kiểm thử biết; **khác** ADMIN_TOKEN |
| `DB_PATH` | `/data/chatbot.db` |

Tạo token mạnh trên Windows: `py -c "import secrets; print(secrets.token_urlsafe(32))"`.

4. **Add Volume** vào service ở đường dẫn mount **`/data`** (bắt buộc nếu muốn lưu dữ liệu khi deploy lại). Chạy **1 replica** vì dùng SQLite. Deploy / Redeploy khi các biến được lưu.
5. Settings -> Networking / Public Networking -> Generate Domain. Railway cấp URL dạng `https://.....up.railway.app`.
6. Mở `/health` kiểm tra `llm_mode=gemini`, `llm_configured=true`; sau đó mở trang chủ. Trình duyệt sẽ yêu cầu **TEAM_USERNAME / TEAM_PASSWORD**.

Nguồn: https://docs.railway.com/quick-start, https://docs.railway.com/volumes, https://docs.railway.com/networking/domains/working-with-domains

## 3. Nạp lại PDF HCMUE 2026 từ máy Windows lên Railway
**Quan trọng:** SQLite local và PDF local không tự chuyển sang Railway khi bạn đẩy code. Khi deploy mới sẽ chưa có tài liệu kích hoạt. Giữ file PDF tuyển sinh 2026 chính thức trên máy; KHÔNG commit tài liệu chưa được kiểm chứng.

Ở thư mục mã nguồn trên máy, đặt thông tin trong `.env` **chỉ ở máy cá nhân**:

```dotenv
ADMIN_TOKEN=GIU_GIONG_GIA_TRI_RAILWAY
TEAM_USERNAME=nhom1
TEAM_PASSWORD=GIU_GIONG_GIA_TRI_RAILWAY
```

Chạy từ PowerShell máy cá nhân (thay URL và đường dẫn PDF thật):

```powershell
.\.venv\Scripts\python.exe scripts/activate_source.py --url https://TEN-DOMAIN.up.railway.app --file HCMUE_SPS_2026.pdf --source-id HCMUE-SPS-2026
```

Nếu chưa có `.venv`, chạy `py -m venv .venv` và `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` trước. Chỉ gõ `DA_DOI_CHIEU` khi đã xác nhận PDF chính thức của SPS năm 2026. Sau đó có thể mở URL để chat, trích dẫn phải có `source_id=HCMUE-SPS-2026`, `mode=gemini`.

**Nếu nạp tài liệu lớn**: server giới hạn 10 MiB/PDF. PDF scan chỉ chứa ảnh không trích được văn bản, cần có bản PDF có text hoặc TXT từ nguồn đã xác minh.

## 4. Kiểm tra bởi 4 thành viên
- Mỗi thành viên nhận **URL + user/pass của nhóm**, không nhận `GEMINI_API_KEY` hoặc `ADMIN_TOKEN`.
- Truy cập trình duyệt, đăng nhập, bấm **Tạo phiên mới** rồi hỏi; dùng `/docs` để kiểm thử API và ghi Expected/Actual/Status trong Excel.
- Dùng `POST /api/sessions` để tạo phiên riêng, lưu `session_id` riêng. Chỉ người quản trị giữ ADMIN_TOKEN để thay tài liệu.
- Với mỗi test AI: kiểm tra HTTP 200, `mode=gemini`, nguồn `HCMUE-SPS-2026`, và đối chiếu **nội dung** với PDF gốc. Có HTTP 200 không đồng nghĩa câu trả lời đúng.
- Các yêu cầu của mọi thành viên sẽ dùng chung quota Gemini. Giữ API key trên server, bật giới hạn chi tiêu/quota và không chia sẻ URL đăng nhập công khai.

## 5. Chạy test local
```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q --cov=app.validators --cov-branch --cov-report=term-missing
```

## 6. Lỗi thường gặp
- `502` / Application failed to respond: xem **Deploy logs**, kiểm tra Start Command `python start_server.py` và `DB_PATH=/data/chatbot.db`, volume đã mount.
- `503 NO_ACTIVE_DOCUMENT`: mới deploy, **chưa upload/kích hoạt PDF trên Railway** (khác với local).
- `401 TEAM_LOGIN_REQUIRED`: chưa đăng nhập hoặc user/pass nhóm sai. `401 UNAUTHORIZED` từ admin: thiếu/sai `X-Admin-Token`.
- `503 LLM_UNAVAILABLE`: mở `/health` kiểm tra key được cấu hình; xem lỗi trong logs và quota Gemini. 429 là có thể đã chạm giới hạn API.
- Dữ liệu mất sau redeploy: kiểm tra có Volume mount `/data` thực sự và `DB_PATH` có bằng `/data/chatbot.db` không.
- Trình duyệt không hỏi lại mật khẩu: HTTP Basic Auth được trình duyệt giữ trong phiên; thử cửa sổ ẩn danh.

## 7. Chi phí và trách nhiệm
Railway Free có 0.5GB volume và $1 credit/tháng sau trial 30 ngày/$5 credit; khi hết credit, service có thể ngừng hoạt động. Ngoài ra Google Gemini API có hạn mức/billing riêng. Bạn không cần trả phí Render nếu chọn Railway, nhưng cần theo dõi Usage của cả hai dịch vụ.

Dự án dùng **mật khẩu chung**, không phải hệ thống tài khoản cá nhân; phù hợp demo nhóm nhỏ nhưng **không nên công bố rộng rãi**. Không đưa dữ liệu cá nhân thật của thí sinh vào chatbot thử nghiệm.
