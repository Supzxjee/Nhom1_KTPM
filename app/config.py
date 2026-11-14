"""App configuration. Read .env locally; secrets are never returned to web clients."""
from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env', override=False)


@dataclass(frozen=True)
class Settings:
    db_path: Path
    majors_csv: Path
    admin_token: str
    llm_mode: str
    openai_api_key: str
    openai_model: str
    gemini_api_key: str
    gemini_model: str
    llm_api_url: str
    llm_api_key: str
    llm_model: str


def get_settings() -> Settings:
    return Settings(
        db_path=Path(os.getenv('DB_PATH', str(ROOT / 'chatbot.db'))),
        majors_csv=Path(os.getenv('MAJORS_CSV', str(ROOT / 'data' / 'majors_2026_HCMUE_SPS_DU_THAO.csv'))),
        admin_token=os.getenv('ADMIN_TOKEN', ''),
        llm_mode=os.getenv('LLM_MODE', 'gemini').strip().lower(),
        openai_api_key=os.getenv('OPENAI_API_KEY', '').strip(),
        openai_model=os.getenv('OPENAI_MODEL', 'gpt-6-luna').strip(),
        gemini_api_key=os.getenv('GEMINI_API_KEY', '').strip(),
        gemini_model=os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite').strip(),
        llm_api_url=os.getenv('LLM_API_URL', '').strip(),
        llm_api_key=os.getenv('LLM_API_KEY', '').strip(),
        llm_model=os.getenv('LLM_MODEL', '').strip(),
    )
