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

def set_col_widths(ws, widths):
    for col_idx, width in enumerate(widths, 1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

# ==========================================
# 1. SHEET: TestCase (TRỐNG HOÀN TOÀN)
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
set_col_widths(ws1, [8, 18, 18, 30, 20, 25, 25, 30, 30, 30, 15, 15, 15, 20])

# ==========================================
# 2. SHEET: RTM (TRỐNG HOÀN TOÀN)
# ==========================================
ws2 = wb.create_sheet(title='RTM')
ws2.views.sheetView[0].showGridLines = True
ws2.cell(row=1, column=1, value='MA TRẬN TRUY VẾT YÊU CẦU - KIỂM THỬ (RTM)').font = font_title
ws2.row_dimensions[1].height = 25

headers2 = [
    'STT', 'Mã yêu cầu', 'Nội dung đặc tả / Quy tắc nghiệp vụ', 'Loại yêu cầu',
    'Mức ưu tiên', 'Mã ca kiểm thử bao phủ (Test Case IDs)', 'Số lượng ca', 'Trạng thái kiểm thử'
]
for col_idx, h in enumerate(headers2, 1):
    ws2.cell(row=3, column=col_idx, value=h)
style_header_row(ws2, 3, len(headers2))
set_col_widths(ws2, [8, 15, 45, 18, 15, 35, 15, 20])

# ==========================================
# 3. SHEET: BaoCaoLoi (TRỐNG HOÀN TOÀN)
# ==========================================
ws3 = wb.create_sheet(title='BaoCaoLoi')
ws3.views.sheetView[0].showGridLines = True
ws3.cell(row=1, column=1, value='BẢNG THEO DÕI BÁO CÁO LỖI (BUG TRACKING LOG)').font = font_title
ws3.row_dimensions[1].height = 25

headers3 = [
    'Mã lỗi', 'Tiêu đề lỗi (Bug Summary)', 'Ca phát hiện', 'Chức năng', 'Môi trường',
    'Mức độ (Severity)', 'Độ ưu tiên (Priority)', 'Trạng thái', 'Người phát hiện',
    'Người xử lý', 'Commit sửa lỗi', 'Ngày báo', 'Ngày đóng'
]
for col_idx, h in enumerate(headers3, 1):
    ws3.cell(row=3, column=col_idx, value=h)
style_header_row(ws3, 3, len(headers3))
set_col_widths(ws3, [12, 35, 15, 15, 18, 18, 18, 15, 18, 18, 25, 15, 15])

# ==========================================
# 4. SHEET: RuiRo (TRỐNG HOÀN TOÀN)
# ==========================================
ws4 = wb.create_sheet(title='RuiRo')
ws4.views.sheetView[0].showGridLines = True
ws4.cell(row=1, column=1, value='MA TRẬN PHÂN TÍCH RỦI RO SẢN PHẨM & DỰ ÁN (RISK MATRIX)').font = font_title
ws4.row_dimensions[1].height = 25

headers4 = [
    'Mã rủi ro', 'Phân loại', 'Mô tả rủi ro tiềm ẩn', 'Khả năng (K: 1-5)',
    'Ảnh hưởng (A: 1-5)', 'Điểm rủi ro (K x A)', 'Mức ưu tiên',
    'Biện pháp phòng ngừa và giảm thiểu', 'Người theo dõi'
]
for col_idx, h in enumerate(headers4, 1):
    ws4.cell(row=3, column=col_idx, value=h)
style_header_row(ws4, 3, len(headers4))
set_col_widths(ws4, [12, 18, 45, 16, 16, 18, 18, 45, 18])

# ==========================================
# 5. SHEET: UocLuong (TRỐNG HOÀN TOÀN)
# ==========================================
ws5 = wb.create_sheet(title='UocLuong')
ws5.views.sheetView[0].showGridLines = True
ws5.cell(row=1, column=1, value='ƯỚC LƯỢNG NỖ LỰC KIỂM THỬ (THREE-POINT ESTIMATION)').font = font_title
ws5.row_dimensions[1].height = 25

headers5 = [
    'STT', 'Công việc kiểm thử chính', 'Lạc quan (O - giờ)', 'Khả dĩ (M - giờ)',
    'Bi quan (P - giờ)', 'Kỳ vọng E = (O+4M+P)/6', 'Độ lệch chuẩn SD = (P-O)/6',
    'Khoảng tin cậy 95% (E ± 2*SD)', 'Người thực hiện'
]
for col_idx, h in enumerate(headers5, 1):
    ws5.cell(row=3, column=col_idx, value=h)
style_header_row(ws5, 3, len(headers5))
set_col_widths(ws5, [8, 45, 18, 18, 18, 22, 22, 25, 20])

# ==========================================
# 6. SHEET: TongKet (KHUNG BÁO CÁO TRỐNG)
# ==========================================
ws6 = wb.create_sheet(title='TongKet')
ws6.views.sheetView[0].showGridLines = True
ws6.cell(row=1, column=1, value='BÁO CÁO TỔNG KẾT KẾT QUẢ KIỂM THỬ (TEST SUMMARY REPORT)').font = font_title
ws6.row_dimensions[1].height = 25

ws6.cell(row=3, column=1, value='1. Thống kê ca kiểm thử theo kỹ thuật').font = font_bold
headers6_1 = ['Kỹ thuật kiểm thử', 'Số lượng ca', 'Pass', 'Fail', 'Blocked', 'Not Run', 'Tỷ lệ đạt (%)']
for col_idx, h in enumerate(headers6_1, 1):
    ws6.cell(row=4, column=col_idx, value=h)
style_header_row(ws6, 4, len(headers6_1), fill=fill_secondary)

techniques = [
    'Phân vùng tương đương (EP) & Giá trị biên (BVA)',
    'Bảng quyết định (Decision Table - FR-03)',
    'Kiểm thử chuyển trạng thái (State Transition - FR-05)',
    'Kiểm thử hộp trắng (validate_query)',
    'Kiểm thử tự động API & Tích hợp',
    'Đánh giá mô hình AI (Golden Set 40 câu)',
    'TỔNG CỘNG'
]
for row_idx, tech in enumerate(techniques, 5):
    ws6.cell(row=row_idx, column=1, value=tech).font = font_bold if tech == 'TỔNG CỘNG' else font_regular
    ws6.cell(row=row_idx, column=1).border = box_border
    for c in range(2, 8):
        cell = ws6.cell(row=row_idx, column=c, value='')
        cell.border = box_border
        cell.alignment = align_center

ws6.cell(row=14, column=1, value='2. Thống kê lỗi phát hiện và xử lý').font = font_bold
headers6_2 = ['Mức độ nghiêm trọng (Severity)', 'Phát hiện', 'Đã sửa (Fixed)', 'Kiểm thử lại đạt (Closed)', 'Tỷ lệ đóng (%)']
for col_idx, h in enumerate(headers6_2, 1):
    ws6.cell(row=15, column=col_idx, value=h)
style_header_row(ws6, 15, len(headers6_2), fill=fill_secondary)

severities = [
    'Critical (Nghiêm trọng - chặn luồng)',
    'Major (Lỗi logic lớn)',
    'Medium (Lỗi trung bình)',
    'Minor (Lỗi nhỏ giao diện/hiển thị)',
    'TỔNG CỘNG LỖI'
]
for row_idx, sev in enumerate(severities, 16):
    ws6.cell(row=row_idx, column=1, value=sev).font = font_bold if sev == 'TỔNG CỘNG LỖI' else font_regular
    ws6.cell(row=row_idx, column=1).border = box_border
    for c in range(2, 6):
        cell = ws6.cell(row=row_idx, column=c, value='')
        cell.border = box_border
        cell.alignment = align_center

set_col_widths(ws6, [45, 15, 12, 12, 12, 12, 18])

# Save
out_file = Path('docs') / 'HoSoKiemThu_Nhom01.xlsx'
wb.save(out_file)
print('100% Blank Excel template generated:', out_file)
