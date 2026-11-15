import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

wb = openpyxl.Workbook()
wb.remove(wb.active)

# Styles
font_title = Font(name='Calibri', size=14, bold=True, color='1F4E78')
font_header = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
font_bold = Font(name='Calibri', size=11, bold=True)
font_regular = Font(name='Calibri', size=11)

fill_primary = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')      # Dark Blue
fill_secondary = PatternFill(start_color='2F5597', end_color='2F5597', fill_type='solid')    # Steel Blue
fill_accent = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')       # Light Soft Blue
fill_pass = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')         # Soft Green
fill_fail = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')         # Soft Red
fill_warn = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')         # Soft Yellow

border_thin = Side(border_style='thin', color='D9D9D9')
box_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)
align_left = Alignment(horizontal='left', vertical='center', wrap_text=True)
align_right = Alignment(horizontal='right', vertical='center')

def style_header_row(ws, row_idx, num_cols, fill=fill_primary):
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row_idx, column=col)
        cell.font = font_header
        cell.fill = fill
        cell.alignment = align_center
        cell.border = box_border
    ws.row_dimensions[row_idx].height = 28

def autofit(ws, max_len_cap=50):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val = str(cell.value or '')
            if cell.row == 1:
                continue
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), max_len_cap)

# ==========================================
# 1. SHEET: TestCase
# ==========================================
ws1 = wb.create_sheet(title='TestCase')
ws1.views.sheetView[0].showGridLines = True
ws1.cell(row=1, column=1, value='DANH MỤC CA KIỂM THỬ (TEST CASES) - HCMUE ADMISSIONS CHATBOT').font = font_title
ws1.row_dimensions[1].height = 25

headers1 = [
    'STT', 'Mã ca kiểm thử', 'Chức năng / Mã YC', 'Tên ca kiểm thử', 'Kỹ thuật áp dụng',
    'Tiền điều kiện', 'Dữ liệu đầu vào (Input)', 'Các bước thực hiện',
    'Kết quả mong đợi', 'Kết quả thực tế', 'Trạng thái', 'Người kiểm thử', 'Ngày chạy', 'Ghi chú'
]
for col_idx, h in enumerate(headers1, 1):
    ws1.cell(row=3, column=col_idx, value=h)
style_header_row(ws1, 3, len(headers1))

sample_tcs = [
    (1, 'TC-CHAT-EP-001', 'FR-01 / BR-01', 'Kiểm tra câu hỏi rỗng sau trim', 'EP (Không hợp lệ)',
     'Phiên hợp lệ, tài liệu active', 'question = ""', '1. Gửi POST /api/chat với question rỗng',
     'HTTP 422, error.code = INVALID_QUESTION', 'HTTP 422, error.code = INVALID_QUESTION', 'Pass', 'Đức Anh', '15/11/2026', 'Biên dưới = 0'),
    (2, 'TC-CHAT-BVA-001', 'FR-01 / BR-01', 'Kiểm tra câu hỏi đạt biên dưới 1 ký tự', 'BVA (Biên hợp lệ)',
     'Phiên hợp lệ, tài liệu active', 'question = "A"', '1. Gửi POST /api/chat với question 1 ký tự',
     'HTTP 200, phản hồi hợp lệ', 'HTTP 200, trả lời hoặc báo thiếu dữ liệu', 'Pass', 'Đức Anh', '15/11/2026', 'Biên n = 1'),
    (3, 'TC-CHAT-BVA-002', 'FR-01 / BR-01', 'Kiểm tra câu hỏi đạt biên trên 500 ký tự', 'BVA (Biên hợp lệ)',
     'Phiên hợp lệ, tài liệu active', 'question = chuỗi 500 ký tự', '1. Gửi POST /api/chat với 500 ký tự',
     'HTTP 200, xử lý bình thường', 'HTTP 200, hệ thống tiếp nhận', 'Pass', 'Đức Anh', '15/11/2026', 'Biên n = 500'),
    (4, 'TC-CHAT-BVA-003', 'FR-01 / BR-01', 'Kiểm tra câu hỏi vượt biên 501 ký tự', 'BVA (Biên không hợp lệ)',
     'Phiên hợp lệ, tài liệu active', 'question = chuỗi 501 ký tự', '1. Gửi POST /api/chat với 501 ký tự',
     'HTTP 422, từ chối trước khi gọi AI', 'HTTP 422, error.code = INVALID_QUESTION', 'Pass', 'Đức Anh', '15/11/2026', 'Biên n = 501'),
    (5, 'TC-MAJOR-BVA-001', 'FR-02 / BR-02', 'Tra cứu mã ngành đúng 7 chữ số tồn tại', 'BVA / Phân vùng',
     'Dataset SPS 2026 đã nạp', 'code = "7140209", year = 2026', '1. Gửi GET /api/majors/7140209?year=2026',
     'HTTP 200, tên ngành Sư phạm Toán học', 'HTTP 200, đúng dữ liệu ngành', 'Pass', 'Đức Anh', '15/11/2026', 'Mã hợp lệ'),
    (6, 'TC-FAV-DEC-001', 'FR-03 / BR-05', 'Thêm ngành quan tâm khi danh sách < 5 và chưa lưu', 'Decision Table (R1)',
     'Phiên hợp lệ, danh sách có 2 ngành', 'major_code = "7140209"', '1. Gửi POST /api/sessions/{id}/favorites',
     'HTTP 200, thêm thành công, count = 3', 'HTTP 200, added = 7140209', 'Pass', 'Bảo Châu', '15/11/2026', 'Quy tắc R1'),
    (7, 'TC-DOC-STA-001', 'FR-05 / BR-06', 'Kích hoạt tài liệu từ trạng thái Nháp (Chuyển bị cấm)', 'State Transition',
     'Có document version ở trạng thái draft', 'POST /api/admin/documents/{id}/activate', '1. Gửi yêu cầu kích hoạt bản nháp',
     'HTTP 409, INVALID_STATE, không cho kích hoạt', 'HTTP 409, INVALID_STATE', 'Pass', 'Bảo Châu', '15/11/2026', 'Chuyển trạng thái cấm'),
    (8, 'TC-WB-CFG-001', 'validate_query', 'Đầu vào question None và major_code None', 'White-box (Branch 1)',
     'Hàm kiểm tra đầu vào', 'question=None, major_code=None', '1. Gọi validate_query()',
     'Lỗi MISSING_INPUT', 'Lỗi MISSING_INPUT', 'Pass', 'Hoàng Thảo', '15/11/2026', 'Đường cơ sở 1'),
]

for row_idx, r in enumerate(sample_tcs, 4):
    for col_idx, val in enumerate(r, 1):
        c = ws1.cell(row=row_idx, column=col_idx, value=val)
        c.font = font_regular
        c.border = box_border
        c.alignment = align_center if col_idx in [1, 2, 3, 5, 11, 13] else align_left
        if col_idx == 11 and val == 'Pass':
            c.fill = fill_pass
    ws1.row_dimensions[row_idx].height = 24
autofit(ws1)

# ==========================================
# 2. SHEET: RTM (Requirements Traceability Matrix)
# ==========================================
ws2 = wb.create_sheet(title='RTM')
ws2.views.sheetView[0].showGridLines = True
ws2.cell(row=1, column=1, value='MA TRẬN TRUY VẾT YÊU CẦU - KIỂM THỬ (RTM)').font = font_title
ws2.row_dimensions[1].height = 25

headers2 = ['STT', 'Mã yêu cầu', 'Nội dung đặc tả / Quy tắc nghiệp vụ', 'Loại yêu cầu', 'Mức ưu tiên', 'Mã ca kiểm thử bao phủ (Test Case IDs)', 'Số lượng ca', 'Trạng thái kiểm thử']
for col_idx, h in enumerate(headers2, 1):
    ws2.cell(row=3, column=col_idx, value=h)
style_header_row(ws2, 3, len(headers2))

sample_rtm = [
    (1, 'FR-01', 'Hỏi đáp tuyển sinh dựa trên tài liệu có dẫn nguồn', 'Chức năng', 'Bắt buộc', 'TC-CHAT-EP-001, TC-CHAT-BVA-001, TC-AI-001..040', 44, 'Đã bao phủ'),
    (2, 'FR-02', 'Tra cứu ngành theo mã 7 chữ số và năm tuyển sinh 2026', 'Chức năng', 'Bắt buộc', 'TC-MAJOR-BVA-001, TC-MAJOR-002..010', 10, 'Đã bao phủ'),
    (3, 'FR-03', 'Thêm/xóa danh sách ngành quan tâm (tối đa 5, không trùng)', 'Chức năng', 'Bắt buộc', 'TC-FAV-DEC-001..008, TC-FAV-BVA-001..004', 12, 'Đã bao phủ'),
    (4, 'FR-04', 'Tạo phiên, xem và xóa lịch sử (giữ nguyên session_id)', 'Chức năng', 'Bắt buộc', 'TC-SESSION-001..008', 8, 'Đã bao phủ'),
    (5, 'FR-05', 'Quản lý phiên bản tài liệu (Nháp -> Kiểm tra -> Đang dùng)', 'Chức năng', 'Bắt buộc', 'TC-DOC-STA-001..010', 10, 'Đã bao phủ'),
    (6, 'BR-01', 'Câu hỏi từ 1 đến 500 ký tự sau khi trim', 'Nghiệp vụ', 'Bắt buộc', 'TC-CHAT-EP-001, TC-CHAT-BVA-001..003', 4, 'Đã bao phủ'),
    (7, 'BR-02', 'Mã ngành tra cứu/lưu bắt buộc là 7 chữ số ASCII', 'Nghiệp vụ', 'Bắt buộc', 'TC-MAJOR-BVA-001, TC-MAJOR-EP-001', 5, 'Đã bao phủ'),
    (8, 'BR-04', 'history_limit từ 0 đến 10, không nhận boolean', 'Nghiệp vụ', 'Bắt buộc', 'TC-HIST-BVA-001..006', 6, 'Đã bao phủ'),
    (9, 'BR-05', 'Danh sách quan tâm tối đa 5 ngành, không trùng', 'Nghiệp vụ', 'Bắt buộc', 'TC-FAV-DEC-001..008', 8, 'Đã bao phủ'),
    (10, 'NFR-08', 'Hàm validate_query() đạt độ bao phủ nhánh >= 80%', 'Phi chức năng', 'Bắt buộc', 'TC-WB-CFG-001..040 (pytest 100% branch)', 40, 'Đã bao phủ'),
]
for row_idx, r in enumerate(sample_rtm, 4):
    for col_idx, val in enumerate(r, 1):
        c = ws2.cell(row=row_idx, column=col_idx, value=val)
        c.font = font_regular
        c.border = box_border
        c.alignment = align_center if col_idx in [1, 2, 4, 5, 7, 8] else align_left
        if col_idx == 8:
            c.fill = fill_pass
    ws2.row_dimensions[row_idx].height = 24
autofit(ws2)

# ==========================================
# 3. SHEET: BaoCaoLoi
# ==========================================
ws3 = wb.create_sheet(title='BaoCaoLoi')
ws3.views.sheetView[0].showGridLines = True
ws3.cell(row=1, column=1, value='BẢNG THEO DÕI BÁO CÁO LỖI (BUG TRACKING LOG)').font = font_title
ws3.row_dimensions[1].height = 25

headers3 = ['Mã lỗi', 'Tiêu đề lỗi (Bug Summary)', 'Ca phát hiện', 'Chức năng', 'Môi trường', 'Mức độ (Severity)', 'Độ ưu tiên (Priority)', 'Trạng thái', 'Người phát hiện', 'Người xử lý', 'Commit sửa lỗi', 'Ngày báo', 'Ngày đóng']
for col_idx, h in enumerate(headers3, 1):
    ws3.cell(row=3, column=col_idx, value=h)
style_header_row(ws3, 3, len(headers3))

sample_bugs = [
    ('BUG-001', 'Lỗi Retrieval v0.7: Không tìm được ngành khi hỏi câu tự nhiên dài có tên ngành', 'TC-AI-001', 'FR-01', 'Railway / Local', 'Critical', 'High', 'Closed', 'Châu', 'Đức Anh', 'fixes #1 (commit 6e4b861)', '14/11/2026', '15/11/2026'),
    ('BUG-002', 'Lỗi 503 NO_ACTIVE_DOCUMENT sau khi redeploy Railway do chưa seed tài liệu', 'TC-DOC-002', 'FR-05', 'Railway', 'Critical', 'High', 'Closed', 'Lâm', 'Đức Anh', 'fixes #2 (commit db20cb4)', '15/11/2026', '15/11/2026'),
    ('BUG-003', 'history_limit nhận giá trị True/False do Python boolean kế thừa int', 'TC-HIST-003', 'FR-04', 'Local/Unit', 'Major', 'Medium', 'Closed', 'Thảo', 'Thảo', 'commit ae3c10a', '14/11/2026', '14/11/2026'),
    ('BUG-004', 'Tra cứu mã chương trình chữ-số (7140202SN) trả về lỗi 500 thay vì 422', 'TC-MAJOR-004', 'FR-02', 'Local/API', 'Major', 'Medium', 'Closed', 'Lâm', 'Đức Anh', 'commit 490109a', '14/11/2026', '14/11/2026'),
    ('BUG-005', 'Xóa lịch sử tin nhắn vô tình xóa luôn phiên session_id', 'TC-SESS-005', 'FR-04', 'Local/API', 'Critical', 'High', 'Closed', 'Châu', 'Đức Anh', 'commit 490109a', '14/11/2026', '14/11/2026'),
    ('BUG-006', 'Thêm ngành quan tâm trùng mã không trả lỗi 409 DUPLICATE_FAVORITE', 'TC-FAV-006', 'FR-03', 'Local/API', 'Medium', 'Medium', 'Closed', 'Lâm', 'Thảo', 'commit 490109a', '14/11/2026', '14/11/2026'),
    ('BUG-007', 'Giao diện web v0.5 không hiển thị phần trích dẫn nguồn khi AI trả lời', 'TC-UI-007', 'UI/FR-01', 'Web Browser', 'Minor', 'Low', 'Closed', 'Đức Anh', 'Đức Anh', 'commit d283938', '14/11/2026', '14/11/2026'),
]
for row_idx, r in enumerate(sample_bugs, 4):
    for col_idx, val in enumerate(r, 1):
        c = ws3.cell(row=row_idx, column=col_idx, value=val)
        c.font = font_regular
        c.border = box_border
        c.alignment = align_center if col_idx in [1, 3, 4, 6, 7, 8, 9, 10, 12, 13] else align_left
        if col_idx == 8 and val == 'Closed':
            c.fill = fill_pass
        elif col_idx == 6 and val == 'Critical':
            c.fill = fill_fail
    ws3.row_dimensions[row_idx].height = 24
autofit(ws3)

# ==========================================
# 4. SHEET: RuiRo
# ==========================================
ws4 = wb.create_sheet(title='RuiRo')
ws4.views.sheetView[0].showGridLines = True
ws4.cell(row=1, column=1, value='MA TRẬN PHÂN TÍCH RỦI RO SẢN PHẨM & DỰ ÁN (RISK MATRIX)').font = font_title
ws4.row_dimensions[1].height = 25

headers4 = ['Mã rủi ro', 'Phân loại', 'Mô tả rủi ro tiềm ẩn', 'Khả năng (K: 1-5)', 'Ảnh hưởng (A: 1-5)', 'Điểm rủi ro (K x A)', 'Mức ưu tiên', 'Biện pháp phòng ngừa và giảm thiểu', 'Người theo dõi']
for col_idx, h in enumerate(headers4, 1):
    ws4.cell(row=3, column=col_idx, value=h)
style_header_row(ws4, 3, len(headers4))

sample_risks = [
    ('SP01', 'Sản phẩm', 'Chatbot bịa đặt (hallucination) học phí hoặc điểm chuẩn 2026 khi thiếu căn cứ', 4, 5, 20, 'Cao (Ưu tiên 1)', 'Cài đặt câu hỏi bẫy; prompt ràng buộc từ chối nếu không có căn cứ', 'Bảo Châu'),
    ('SP02', 'Sản phẩm', 'Nhầm lẫn thông tin giữa các năm tuyển sinh hoặc nhầm mã ngành 7 số', 3, 5, 15, 'Cao (Ưu tiên 2)', 'Khóa dataset chỉ nhận năm 2026; regex mã 7 chữ số tại API validation', 'Đức Anh'),
    ('SP03', 'Sản phẩm', 'Prompt Injection khiến mô hình bỏ qua tài liệu hoặc tiết lộ API key', 3, 5, 15, 'Cao (Ưu tiên 3)', 'Kiểm thử 5 ca injection; không truyền API key vào prompt hệ thống', 'Châu Kiến Lâm'),
    ('SP04', 'Sản phẩm', 'Trích dẫn nguồn không tương thích hoặc không khớp với nội dung trả lời', 4, 4, 16, 'Cao (Ưu tiên 4)', 'RAG chỉ trích xuất đoạn có score cao; kiểm tra chéo citation ID với document', 'Lê Việt Hoàng Thảo'),
    ('DA01', 'Dự án', 'Dữ liệu tuyển sinh 2026 bị thay đổi, phải làm lại đáp án tham chiếu', 4, 4, 16, 'Cao (Ưu tiên 5)', 'Khóa cứng tài liệu HCMUE_SPS_2026.pdf phiên bản chuẩn ngay từ đầu', 'Đức Anh'),
    ('DA02', 'Dự án', 'Hết quota Gemini API hoặc lỗi mạng làm gián đoạn kiểm thử tự động', 3, 4, 12, 'Trung bình', 'Dùng Mock LLM cho toàn bộ Unit/API test; chỉ gọi API thật khi test 40 câu AI', 'Châu Kiến Lâm'),
]
for row_idx, r in enumerate(sample_risks, 4):
    for col_idx, val in enumerate(r, 1):
        c = ws4.cell(row=row_idx, column=col_idx, value=val)
        c.font = font_regular
        c.border = box_border
        c.alignment = align_center if col_idx in [1, 2, 4, 5, 6, 7, 9] else align_left
        if col_idx == 7 and 'Cao' in str(val):
            c.fill = fill_fail
        elif col_idx == 7 and 'Trung bình' in str(val):
            c.fill = fill_warn
    ws4.row_dimensions[row_idx].height = 24
autofit(ws4)

# ==========================================
# 5. SHEET: UocLuong
# ==========================================
ws5 = wb.create_sheet(title='UocLuong')
ws5.views.sheetView[0].showGridLines = True
ws5.cell(row=1, column=1, value='ƯỚC LƯỢNG NỖ LỰC KIỂM THỬ (THREE-POINT ESTIMATION)').font = font_title
ws5.row_dimensions[1].height = 25

headers5 = ['STT', 'Công việc kiểm thử chính', 'Lạc quan (O - giờ)', 'Khả dĩ (M - giờ)', 'Bi quan (P - giờ)', 'Kỳ vọng E = (O+4M+P)/6', 'Độ lệch chuẩn SD = (P-O)/6', 'Khoảng tin cậy 95% (E ± 2*SD)', 'Người thực hiện']
for col_idx, h in enumerate(headers5, 1):
    ws5.cell(row=3, column=col_idx, value=h)
style_header_row(ws5, 3, len(headers5))

sample_estimates = [
    (1, 'Phân tích yêu cầu & Thiết kế bộ ca kiểm thử hộp đen (EP/BVA, Decision Table, State)', 12, 18, 30, 'Đức Anh, Châu'),
    (2, 'Phân tích hộp trắng hàm validate_query() (CFG, V(G), basis paths, pytest branch 100%)', 8, 12, 20, 'Hoàng Thảo'),
    (3, 'Thực nghiệm bộ 40 câu hỏi AI (chạy lặp 3 lần = 120 lượt), phân tích lỗi & viết báo cáo', 10, 16, 26, 'Bảo Châu, Lâm'),
    (4, 'Xây dựng kịch bản kiểm thử tự động API/UI và thiết lập CI GitHub Actions', 8, 14, 22, 'Kiến Lâm, Thảo'),
    (5, 'Kiểm thử hồi quy, quản lý lỗi (7 issue) và hoàn thiện tiểu luận 25-40 trang + video', 16, 24, 38, 'Cả nhóm'),
]

for row_idx, r in enumerate(sample_estimates, 4):
    stt, task, o, m, p, owner = r
    e_val = round((o + 4*m + p)/6, 2)
    sd_val = round((p - o)/6, 2)
    ci_val = f'{round(e_val - 2*sd_val, 1)}h - {round(e_val + 2*sd_val, 1)}h'
    row_data = [stt, task, o, m, p, e_val, sd_val, ci_val, owner]
    for col_idx, val in enumerate(row_data, 1):
        c = ws5.cell(row=row_idx, column=col_idx, value=val)
        c.font = font_regular
        c.border = box_border
        c.alignment = align_center if col_idx in [1, 3, 4, 5, 6, 7, 8, 9] else align_left
        if col_idx == 6:
            c.font = font_bold
            c.fill = fill_accent
    ws5.row_dimensions[row_idx].height = 24
autofit(ws5)

# ==========================================
# 6. SHEET: TongKet
# ==========================================
ws6 = wb.create_sheet(title='TongKet')
ws6.views.sheetView[0].showGridLines = True
ws6.cell(row=1, column=1, value='BÁO CÁO TỔNG KẾT KẾT QUẢ KIỂM THỬ (TEST SUMMARY REPORT)').font = font_title
ws6.row_dimensions[1].height = 25

# Summary Table 1
ws6.cell(row=3, column=1, value='1. Thống kê ca kiểm thử theo kỹ thuật').font = font_bold
headers6_1 = ['Kỹ thuật kiểm thử', 'Số lượng ca', 'Pass', 'Fail', 'Blocked', 'Tỷ lệ đạt (%)']
for col_idx, h in enumerate(headers6_1, 1):
    ws6.cell(row=4, column=col_idx, value=h)
style_header_row(ws6, 4, len(headers6_1), fill=fill_secondary)

t1_data = [
    ('Phân vùng tương đương (EP) & Giá trị biên (BVA)', 36, 36, 0, 0, '100%'),
    ('Bảng quyết định (Decision Table - FR-03)', 8, 8, 0, 0, '100%'),
    ('Kiểm thử chuyển trạng thái (State Transition - FR-05)', 10, 10, 0, 0, '100%'),
    ('Kiểm thử hộp trắng (validate_query - Branch coverage)', 40, 40, 0, 0, '100%'),
    ('Kiểm thử tự động API & Tích hợp (pytest/HTTPX)', 33, 33, 0, 0, '100%'),
    ('Đánh giá mô hình AI (Golden Set 40 câu x 3 lượt = 120 lần)', 120, 108, 12, 0, '90.0% (Mục tiêu >= 85%)'),
    ('TỔNG CỘNG', 247, 235, 12, 0, '95.1%')
]
for row_idx, r in enumerate(t1_data, 5):
    for col_idx, val in enumerate(r, 1):
        c = ws6.cell(row=row_idx, column=col_idx, value=val)
        c.font = font_bold if row_idx == 11 else font_regular
        c.border = box_border
        c.alignment = align_center if col_idx in [2, 3, 4, 5, 6] else align_left
        if row_idx == 11:
            c.fill = fill_accent
    ws6.row_dimensions[row_idx].height = 24

# Summary Table 2: Bug statistics
ws6.cell(row=13, column=1, value='2. Thống kê lỗi phát hiện và xử lý').font = font_bold
headers6_2 = ['Mức độ nghiêm trọng (Severity)', 'Phát hiện', 'Đã sửa (Fixed)', 'Kiểm thử lại đạt (Closed)', 'Tỷ lệ đóng (%)']
for col_idx, h in enumerate(headers6_2, 1):
    ws6.cell(row=14, column=col_idx, value=h)
style_header_row(ws6, 14, len(headers6_2), fill=fill_secondary)

t2_data = [
    ('Critical (Nghiêm trọng - chặn luồng)', 3, 3, 3, '100%'),
    ('Major (Lỗi logic lớn)', 2, 2, 2, '100%'),
    ('Medium (Lỗi trung bình)', 1, 1, 1, '100%'),
    ('Minor (Lỗi nhỏ giao diện/hiển thị)', 1, 1, 1, '100%'),
    ('TỔNG CỘNG LỖI', 7, 7, 7, '100%')
]
for row_idx, r in enumerate(t2_data, 15):
    for col_idx, val in enumerate(r, 1):
        c = ws6.cell(row=row_idx, column=col_idx, value=val)
        c.font = font_bold if row_idx == 19 else font_regular
        c.border = box_border
        c.alignment = align_center if col_idx in [2, 3, 4, 5] else align_left
        if row_idx == 19:
            c.fill = fill_accent
    ws6.row_dimensions[row_idx].height = 24

# Summary Table 3: Conclusion
ws6.cell(row=21, column=1, value='3. Kết luận đánh giá').font = font_bold
ws6.cell(row=22, column=1, value='- Hệ thống đạt 100% tiêu chí chức năng FR-01 đến FR-05, không còn lỗi mức Critical/Major tồn đọng.').font = font_regular
ws6.cell(row=23, column=1, value='- Độ bao phủ nhánh hộp trắng hàm validate_query() đạt 100% (vượt mục tiêu >= 80% của SRS).').font = font_regular
ws6.cell(row=24, column=1, value='- Tỷ lệ đạt của bộ câu hỏi AI đạt 90.0% (108/120 lượt đạt theo rubric 4 tiêu chí, vượt ngưỡng nghiệm thu >= 85%).').font = font_regular
ws6.cell(row=25, column=1, value='- Khuyến nghị: Đủ điều kiện nghiệm thu và phát hành phiên bản thử nghiệm cho sinh viên môn COMP1307.').font = font_bold

autofit(ws6)

# Save
out_dir = Path('docs')
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / 'HoSoKiemThu_Nhom01.xlsx'
wb.save(out_file)
print('Successfully generated:', out_file)
