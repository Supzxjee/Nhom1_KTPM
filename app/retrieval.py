"""Minimal lexical retrieval. Upgrade later to BM25/embeddings with a fixed evaluation set."""
import io
import re
import unicodedata
from pypdf import PdfReader

STOP = {'la','co','ve','cua','toi','cho','hoi','muon','nhung','nam','nao','duoc','thi','va','truong',
        'dai','hoc','tuyen','sinh','thong','tin','o','the','khong','nhu','bao','nhieu','nganh'}


def text_from_upload(filename: str, content: bytes):
    name = filename.lower()
    if name.endswith('.txt'):
        try:
            text = content.decode('utf-8-sig')
        except UnicodeDecodeError as exc:
            raise ValueError('TXT phải là UTF-8.') from exc
    elif name.endswith('.pdf'):
        try:
            reader = PdfReader(io.BytesIO(content))
            text = '\n'.join(page.extract_text() or '' for page in reader.pages)
        except Exception as exc:
            raise ValueError('PDF không hợp lệ hoặc không đọc được.') from exc
    else:
        raise ValueError('Chỉ hỗ trợ PDF/TXT.')
    if not text.strip():
        raise ValueError('Tài liệu không có văn bản trích xuất được (PDF scan cần OCR).')
    return text.strip()


def tokenize(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    terms = re.findall(r'[a-z0-9]{2,}', s)
    return set(terms) - STOP


def chunks(text, max_chars=1100):
    """Split on paragraphs then cap each chunk; no external embeddings required."""
    parts = re.split(r'\n\s*\n', text)
    result = []
    for part in parts:
        part = part.strip()
        while part:
            result.append(part[:max_chars])
            part = part[max_chars:].strip()
    return result


def retrieve(question, text, top_k=3):
    q = tokenize(question)
    if not q:
        return []
    scored = []
    for i, chunk in enumerate(chunks(text), 1):
        match = len(q & tokenize(chunk))
        if match > 0:
            scored.append((match, i, chunk))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [{'section': f'Đoạn {idx}', 'excerpt': ch, 'match_terms': score}
            for score, idx, ch in scored[:top_k]]
