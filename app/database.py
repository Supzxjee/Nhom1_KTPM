"""SQLite schema and non-destructive import of the draft HCMUE dataset."""
import csv
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS majors (
    official_program_code TEXT NOT NULL,
    major_code_7 TEXT,
    major_name TEXT NOT NULL,
    admission_year INTEGER NOT NULL,
    campus_code TEXT NOT NULL,
    program_label TEXT,
    program_group TEXT,
    source_id TEXT NOT NULL,
    document_version_id TEXT NOT NULL,
    dataset_status TEXT NOT NULL,
    source_url TEXT,
    notes TEXT,
    PRIMARY KEY (official_program_code, admission_year, campus_code)
);
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    citations_json TEXT NOT NULL DEFAULT '[]',
    document_version_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS favorites (
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    major_code TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, major_code)
);
CREATE TABLE IF NOT EXISTS document_versions (
    version_id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL DEFAULT 'SPS_2026',
    source_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft','verified','active','replaced')),
    text_content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TEXT,
    activated_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_version
    ON document_versions(dataset_id) WHERE status='active';
'''

@contextmanager
def db_connect(path):
    con = sqlite3.connect(str(path), timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    try:
        yield con
        con.commit()
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()


def initialize(db_path: Path, majors_csv: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with db_connect(db_path) as conn:
        conn.executescript(SCHEMA)
        with majors_csv.open(encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                if row.get('campus_code') != 'SPS':
                    continue
                conn.execute('''INSERT OR IGNORE INTO majors
                    (official_program_code,major_code_7,major_name,admission_year,campus_code,
                     program_label,program_group,source_id,document_version_id,dataset_status,source_url,notes)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', (
                    row['official_program_code'], row['major_code_7'] or None, row['major_name'],
                    int(row['admission_year']), row['campus_code'], row['program_label'],
                    row['program_group'], row['source_id'], row['document_version_id'],
                    row['dataset_status'], row['source_url'], row['notes'],
                ))
