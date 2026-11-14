"""Retrieval v0.7 – weighted lexical search with major-code boosting.

Upgrade path: replace score() with BM25 / dense embeddings once a fixed
evaluation set is established.  The public API (retrieve, text_from_upload,
expand_query_with_catalog) must stay stable so test_retrieval_regression.py
keeps passing.
"""
import io
import re
import unicodedata
from pypdf import PdfReader

# ---------------------------------------------------------------------------
# Stop-words (Vietnamese + generic recruitment terms that add noise)
# ---------------------------------------------------------------------------
STOP = {
    'la', 'co', 've', 'cua', 'toi', 'cho', 'hoi', 'muon', 'nhung', 'nam',
    'nao', 'duoc', 'thi', 'va', 'truong', 'dai', 'hoc', 'tuyen', 'sinh',
    'thong', 'tin', 'o', 'the', 'khong', 'nhu', 'bao', 'nhieu', 'nganh',
}

# Weight multiplier when a 7-digit major code appears in both query and chunk.
_CODE_BOOST = 8
# Weight multiplier for every catalogue name token that appears in both.
_NAME_BOOST = 2
# Proximity bonus for chunks adjacent (±2) to a code-matching chunk.
_PROXIMITY_BOOST = 7


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def text_from_upload(filename: str, content: bytes) -> str:
    """Extract plain text from a PDF or UTF-8 TXT upload."""
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


def _normalize(s: str) -> str:
    """NFD-normalise and strip diacritics → ASCII-ish lowercase."""
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def tokenize(s: str) -> set[str]:
    terms = re.findall(r'[a-z0-9]{2,}', _normalize(s))
    return set(terms) - STOP


def _extract_7digit_codes(s: str) -> set[str]:
    """Return all 7-digit numeric strings found in *s*."""
    return set(re.findall(r'\b\d{7}\b', s))


def chunks(text: str, max_chars: int = 1100) -> list[str]:
    """Split on blank lines then hard-cap each chunk."""
    parts = re.split(r'\n\s*\n', text)
    result: list[str] = []
    for part in parts:
        part = part.strip()
        while part:
            result.append(part[:max_chars])
            part = part[max_chars:].strip()
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def expand_query_with_catalog(
    question: str,
    catalog: list[tuple[str, str]],
) -> str:
    """Inject matching major codes into *question* to boost retrieval.

    Parameters
    ----------
    question:
        Raw natural-language question from the user.
    catalog:
        List of (major_name, major_code_7) pairs from the DB.

    Returns
    -------
    Augmented query string.  If no catalogue entry matches, the original
    question is returned unchanged.
    """
    q_norm = _normalize(question)
    injected: list[str] = []
    for name, code in catalog:
        if not name or not code:
            continue
        # Match if every significant token of the name appears in the question.
        name_tokens = tokenize(name)
        if name_tokens and name_tokens.issubset(tokenize(question)):
            injected.append(code)
        # Also match by normalised substring (handles diacritic variants).
        elif _normalize(name) in q_norm:
            injected.append(code)
    if injected:
        return question + ' ' + ' '.join(injected)
    return question


def retrieve(
    question: str,
    text: str,
    top_k: int = 5,
    catalog: list[tuple[str, str]] | None = None,
) -> list[dict]:
    """Return up to *top_k* most relevant chunks from *text*.

    Scoring (additive):
    - Base: number of overlapping non-stop tokens between query and chunk.
    - Code boost: ``_CODE_BOOST`` points for each 7-digit code shared between
      the (possibly expanded) query and the chunk.
    - Name boost: ``_NAME_BOOST`` extra points per name-token that hits, for
      catalogue entries whose name appeared in the question.
    """
    # Expand query with catalogue codes when available.
    if catalog:
        question = expand_query_with_catalog(question, catalog)

    q_tokens = tokenize(question)
    q_codes = _extract_7digit_codes(question)

    if not q_tokens and not q_codes:
        return []

    # Pre-compute which catalogue names matched so we can boost their tokens.
    name_boost_tokens: set[str] = set()
    if catalog:
        for name, code in catalog:
            if code in q_codes and name:
                name_boost_tokens |= tokenize(name)

    all_chunks = chunks(text)
    # First pass: compute raw scores and find code-matching chunk indices.
    raw: list[tuple[float, int, str]] = []
    code_match_indices: set[int] = set()   # 1-based
    for i, chunk in enumerate(all_chunks, 1):
        c_tokens = tokenize(chunk)
        c_codes = _extract_7digit_codes(chunk)

        base = len(q_tokens & c_tokens)
        code_score = len(q_codes & c_codes) * _CODE_BOOST
        name_score = len(name_boost_tokens & c_tokens) * _NAME_BOOST

        total = base + code_score + name_score
        raw.append((total, i, chunk))
        if code_score > 0:
            code_match_indices.add(i)

    # Second pass: proximity boost for chunks adjacent (±2) to code-matched ones.
    scored: list[tuple[float, int, str]] = []
    for total, i, chunk in raw:
        if any(abs(i - ci) <= 2 for ci in code_match_indices):
            total += _PROXIMITY_BOOST
        if total > 0:
            scored.append((total, i, chunk))

    scored.sort(key=lambda x: (-x[0], x[1]))
    return [
        {'section': f'Đoạn {idx}', 'excerpt': ch, 'match_terms': score}
        for score, idx, ch in scored[:top_k]
    ]
