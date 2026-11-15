---
name: Báo cáo lỗi (Bug Report)
about: Tạo báo cáo lỗi phát hiện trong quá trình kiểm thử phần mềm
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

### 1. Thông tin chung
- **Mã lỗi (Bug ID):** BUG-XXX
- **Ca kiểm thử liên quan (Test Case ID):** TC-XXX
- **Chức năng bị ảnh hưởng:** [FR-01 / FR-02 / FR-03 / FR-04 / FR-05 / Khác]
- **Người phát hiện:** [Họ tên thành viên]
- **Ngày phát hiện:** DD/MM/2026

### 2. Môi trường kiểm thử
- **Môi trường:** [Railway (https://hcmuehub.online) / Localhost]
- **Hệ điều hành / Thiết bị:** [Windows 11 / macOS / Ubuntu]
- **Trình duyệt / Công cụ gọi API:** [Chrome / Edge / Postman / Pytest / HTTPX]
- **Phiên bản ứng dụng:** [v0.7.0 / Commit hash]
- **Tài liệu tuyển sinh đang active:** [HCMUE-SPS-2026 / DV-SEED-HCMUE_SP]

### 3. Đánh giá mức độ
- **Mức độ nghiêm trọng (Severity):** [Critical / Major / Medium / Minor]
  - *Critical:* Hệ thống sập, treo, bảo mật lộ key, mất dữ liệu phiên.
  - *Major:* Sai logic nghiệp vụ chính, AI bịa đặt dữ liệu (hallucination) nghiêm trọng.
  - *Medium:* Lỗi hiển thị, sai mã HTTP, xử lý biên chưa chuẩn nhưng có workaround.
  - *Minor:* Lỗi chính tả, định dạng giao diện nhỏ.
- **Mức độ ưu tiên sửa (Priority):** [High / Medium / Low]
- **Tần suất lặp lại (Frequency):** [100% (luôn xảy ra) / ~50% (thỉnh thoảng) / Khó tái hiện]

---

### 4. Chi tiết lỗi

#### Các bước tái hiện (Steps to Reproduce):
1. Truy cập vào ...
2. Nhập dữ liệu: `...`
3. Thực hiện thao tác: `...`

#### Kết quả mong đợi (Expected Result):
- [Mô tả hệ thống nên phản hồi như thế nào theo SRS / đặc tả]

#### Kết quả thực tế (Actual Result):
- [Mô tả hệ thống thực tế đang phản hồi ra sao / kèm mã lỗi HTTP]

---

### 5. Minh chứng (Evidence)
- **Ảnh chụp màn hình / Video:**
  *(Dán ảnh chụp màn hình hoặc link video tại đây)*
- **Log máy chủ / API Response:**
  ```json
  // Dán log hoặc response JSON nếu có
  ```

---

### 6. Phân tích nguyên nhân gốc & Sửa lỗi (Dành cho người fix)
- **Nguyên nhân kỹ thuật (Root Cause / 5 Whys):**
  - Tại sao 1: ...
  - Tại sao 2: ...
  - Tại sao 3: ...
- **Commit sửa lỗi:** `fixes #...`
- **Kết quả kiểm thử hồi quy (Retest Result):** [Pass / Fail]
