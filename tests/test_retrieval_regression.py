"""Regression tests: natural language question vs programme-code lookup."""
from app.retrieval import expand_query_with_catalog, retrieve


def test_full_natural_question_resolves_to_code():
    question = 'Ngành Sư phạm Toán học năm 2026 có bao nhiêu chỉ tiêu và các tổ hợp xét tuyển nào?'
    expanded = expand_query_with_catalog(question, [
        ('Sư phạm Toán học', '7140209'), ('Sư phạm Ngữ văn', '7140217')])
    assert '7140209' in expanded
    assert '7140217' not in expanded


def test_code_outweighs_generic_repeated_recruitment_terms():
    text = '\n\n'.join([
        'Năm 2026 có phương thức xét tuyển, chỉ tiêu và tổ hợp xét tuyển cho thí sinh.'
        for _ in range(12)
    ] + [
        'Ngành Sư phạm Toán học mã 7140209. Chỉ tiêu 140. Tổ hợp A00.',
        'Tổ hợp A01 và X06. Ưu tiên xét tuyển.',
        'Tổ hợp A00TO, A01TO, X06TO kết hợp ĐGNLCB.'
    ])
    q = 'Ngành Sư phạm Toán học năm 2026 có bao nhiêu chỉ tiêu và các tổ hợp xét tuyển nào?'
    q = expand_query_with_catalog(q, [('Sư phạm Toán học', '7140209')])
    matches = retrieve(q, text)
    assert matches[0]['section'] == 'Đoạn 13'
    assert any('A01TO' in x['excerpt'] for x in matches)
    assert all('Đoạn' in x['section'] for x in matches)


def test_unknown_code_does_not_fall_back_to_unrelated_major():
    text = 'Ngành Sư phạm Toán học, mã 7140209, có 140 chỉ tiêu năm 2026.'
    assert retrieve('1234567', text) == []


def test_generic_question_still_retrieves_without_major_code():
    text = 'Thời tiết đẹp.\n\nXét tuyển thẳng thí sinh theo quy chế tuyển sinh năm 2026.'
    results = retrieve('Xét tuyển thẳng áp dụng như thế nào?', text)
    assert results and 'Xét tuyển thẳng' in results[0]['excerpt']
