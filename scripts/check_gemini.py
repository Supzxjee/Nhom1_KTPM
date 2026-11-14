"""Safely check configured Gemini key and model with a tiny live call (may incur costs)."""
from pathlib import Path
import sys
import httpx

# Script can run as `python scripts/check_gemini.py` from project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import get_settings

s = get_settings()
print('LLM_MODE:', s.llm_mode)
print('GEMINI_MODEL:', s.gemini_model)
print('GEMINI_API_KEY:', 'ĐÃ CẤU HÌNH' if s.gemini_api_key else 'CHƯA CÓ')
if not s.gemini_api_key:
    raise SystemExit('Thiếu GEMINI_API_KEY trong .env')

url = f'https://generativelanguage.googleapis.com/v1beta/models/{s.gemini_model}:generateContent'
try:
    r = httpx.post(url, headers={'x-goog-api-key':s.gemini_api_key},
        json={'contents':[{'parts':[{'text':'Hãy trả lời đúng một từ: OK'}]}],
              'generationConfig':{'maxOutputTokens':100}}, timeout=40)
except httpx.HTTPError as err:
    raise SystemExit(f'Không kết nối được Gemini: {type(err).__name__}') from None

print('HTTP:', r.status_code)
if r.is_error:
    print('Kiểm tra API key / model / quyền / hạn mức trên Google AI Studio. Không chia sẻ khóa.')
else:
    try:
        from app.llm import _parse_gemini_text
        print('Phản hồi:', _parse_gemini_text(r.json())[:200])
    except (ValueError, RuntimeError, KeyError, TypeError):
        print('API kết nối được nhưng không có nội dung văn bản trong phản hồi.')
