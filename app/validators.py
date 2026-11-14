"""A deliberately isolated function for white-box CFG, V(G), and branch testing."""
import re


def validate_query(question=None, major_code=None, admission_year=2026, history_limit=5):
    """Return list of structured error dicts; empty list means valid.

    Optional question and major_code support separate chat / lookup operations.
    At least one of these fields must be provided. Boolean is NOT an integer input.
    """
    errors = []
    if question is None and major_code is None:
        errors.append({'field': 'question', 'code': 'MISSING_INPUT', 'message': 'Cần câu hỏi hoặc mã ngành.'})

    if question is not None:
        if not isinstance(question, str):
            errors.append({'field': 'question', 'code': 'INVALID_TYPE', 'message': 'Câu hỏi phải là chuỗi.'})
        else:
            n = len(question.strip())
            if n < 1 or n > 500:
                errors.append({'field': 'question', 'code': 'INVALID_QUESTION', 'message': 'Câu hỏi phải dài 1–500 ký tự sau trim.'})

    if major_code is not None:
        if not isinstance(major_code, str):
            errors.append({'field': 'major_code', 'code': 'INVALID_TYPE', 'message': 'Mã ngành phải là chuỗi.'})
        elif not re.fullmatch(r'[0-9]{7}', major_code):
            errors.append({'field': 'major_code', 'code': 'INVALID_MAJOR_CODE', 'message': 'Mã tra cứu phải là 7 chữ số ASCII.'})

    if isinstance(admission_year, bool) or not isinstance(admission_year, int) or admission_year != 2026:
        errors.append({'field': 'admission_year', 'code': 'INVALID_YEAR', 'message': 'Phiên bản này chỉ hỗ trợ năm 2026 (số nguyên).'})

    if isinstance(history_limit, bool) or not isinstance(history_limit, int):
        errors.append({'field': 'history_limit', 'code': 'INVALID_TYPE', 'message': 'history_limit phải là số nguyên.'})
    elif not 0 <= history_limit <= 10:
        errors.append({'field': 'history_limit', 'code': 'INVALID_HISTORY_LIMIT', 'message': 'history_limit phải từ 0 đến 10.'})
    return errors
