# Kế hoạch kiểm thử nháp chatbot tư vấn tuyển sinh

Nhóm 1 · Lớp 49.CNTTA · Hướng C · Dự kiến trước Buổi 4

## 1 Mục tiêu và phạm vi

Kiểm tra chatbot trả lời đúng tài liệu, có nguồn hỗ trợ và xử lý đúng đầu vào, phiên hội thoại, quyền quản trị. Nhóm 4 người dự kiến có ít nhất 80 ca thủ công, 20 unit test, 10 kịch bản UI/API; bộ AI ít nhất 40 câu, mỗi câu chạy ít nhất 3 lần, có ít nhất 10 câu bẫy và 5 ca prompt injection theo hướng dẫn.

Trong phạm vi: hỏi đáp có dẫn nguồn; tra cứu ngành theo mã/năm; thêm/xóa tối đa 5 ngành quan tâm; tạo/xem/xóa lịch sử phiên; nạp và kích hoạt tài liệu bởi quản trị viên. Dữ liệu giới hạn ở một trường, một năm và một bộ tài liệu có phiên bản.

Ngoài phạm vi: cổng tuyển sinh thật của trường, huấn luyện mô hình nền và dự đoán khả năng trúng tuyển.

## 2 Cách tiếp cận

Đối chiếu yêu cầu và đáp án tham chiếu với tài liệu nguồn. Dùng EP/BVA cho câu hỏi, mã ngành, history_limit; bảng quyết định cho lưu ngành; chuyển trạng thái cho tài liệu. Kiểm thử hộp trắng 1 hàm đầu vào/đầu ra theo hướng C; kiểm tra unit, UI/API và hồi quy sau sửa lỗi. Với AI, đánh giá tính đúng, nguồn hỗ trợ, xử lý thiếu căn cứ và injection qua các lượt chạy lặp.

Công cụ dự kiến: pytest, pytest-cov, HTTPX/Playwright, GitHub Actions, GitHub Issues và Excel theo phiếu đăng ký.

## 3 Tiêu chí đầu vào và đầu ra

Đầu vào đề xuất: (1) chốt phạm vi, yêu cầu và bộ nguồn; (2) có bản chạy, môi trường và dữ liệu giả; (3) ca kiểm thử có kết quả mong đợi và đáp án tham chiếu được nhóm rà soát.

Đầu ra đề xuất: (1) đủ số ca và lượt chạy ở mục 1, có kết quả và RTM; (2) đạt ít nhất 90% lượt AI theo tiêu chí trong phiếu đăng ký, không có lượt lộ bí mật giả hoặc bịa thông tin tuyển sinh trọng yếu; (3) có hồ sơ lỗi thật, minh chứng kiểm thử xác nhận/hồi quy và nêu rõ phần chưa đạt.

<!-- pagebreak -->

## 4 Rủi ro dự kiến

K: khả năng; A: ảnh hưởng, thang 1–5. Điểm là đề xuất của bản nháp. SP: sản phẩm; DA: dự án.

| Mã | Rủi ro | K | A | K × A | Biện pháp |
|---|---|---|---|---|---|
| SP01 | Bịa học phí hoặc điểm chuẩn khi thiếu căn cứ. | 4 | 5 | 20 | Câu hỏi bẫy; đối chiếu nguồn. |
| SP02 | Nhầm năm tuyển sinh hoặc mã ngành. | 3 | 5 | 15 | Đổi năm/mã; kiểm tra ngữ cảnh. |
| SP03 | Injection khiến bỏ quy tắc hoặc lộ bí mật giả. | 3 | 5 | 15 | Thử ở câu hỏi và tài liệu. |
| SP04 | Nguồn dẫn không hỗ trợ câu trả lời. | 4 | 4 | 16 | Đối chiếu từng khẳng định. |
| DA01 | Chưa chốt nguồn, phải làm lại đáp án. | 4 | 4 | 16 | Chốt và lưu phiên bản nguồn. |
| DA02 | Hết hạn mức API làm chậm đợt chạy. | 3 | 4 | 12 | Kiểm tra hạn mức, chia đợt chạy. |

Ưu tiên các rủi ro mức cao 15–25; mức 8–14 là trung bình, 1–7 là thấp theo phiếu Buổi 3.

## 5 Phân công đề xuất

| Thành viên | MSSV | Phụ trách |
|---|---|---|
| Lê Đức Anh | 49.01.104.002 | Yêu cầu, EP/BVA, RTM, kế hoạch. |
| Trần Bảo Châu | 49.01.104.013 | Bảng quyết định, trạng thái, câu AI. |
| Lê Việt Hoàng Thảo | 47.01.104.196 | Hộp trắng, unit test, CI. |
| Châu Kiến Lâm | 50.01.104.082 | UI/API, lỗi, hồi quy, rủi ro. |

## 6 Lịch dự kiến

Trước Buổi 4: phiếu đăng ký lên LMS, kế hoạch nháp lên GitHub. Buổi 4–6: chốt nguồn, đặc tả và thiết kế ca. Buổi 7: nộp kế hoạch và Excel, có ít nhất 50% số ca và RTM sơ bộ. Buổi 7–9: hộp trắng, thực thi, unit test và CI. Buổi 10: tự động UI/API, hồi quy, báo cáo, slide và video. Hạn cuối: 23:59, 7 ngày sau Buổi 10.

Cần bổ sung: trường/năm, bộ nguồn, link GitHub, ngày học cụ thể; nhóm xác nhận phân công. Các thông tin này chưa chốt nên để trống.

Căn cứ: phiếu Buổi 3, Bài nhóm 3.2; hướng dẫn tiểu luận mục 2 và 3.5–3.6; phiếu đăng ký chatbot của nhóm.
