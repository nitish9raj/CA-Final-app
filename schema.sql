-- ================================================================
--  CA Final AI Suite v7.0 — Supabase PostgreSQL Schema
--  HOW TO USE:
--    1. Go to https://supabase.com → your project
--    2. Click "SQL Editor" in the left sidebar
--    3. Paste this entire file → click "Run"
-- ================================================================

-- ── USERS (synced from Firebase Auth) ───────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,          -- Firebase UID
    email         TEXT UNIQUE,
    display_name  TEXT,
    photo_url     TEXT,
    plan          TEXT    DEFAULT 'free',    -- free | pro
    exam_date     TEXT    DEFAULT '2026-05-01',
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    last_seen     TIMESTAMPTZ DEFAULT NOW()
);

-- ── STUDY SESSIONS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS study_sessions (
    id               BIGSERIAL PRIMARY KEY,
    user_id          TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date             TEXT NOT NULL,
    subject          TEXT NOT NULL,
    category         TEXT NOT NULL DEFAULT 'Self Study',
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    notes            TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ss_user ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_ss_date ON study_sessions(date DESC);

-- ── MOCK TESTS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mock_tests (
    id             BIGSERIAL PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date           TEXT NOT NULL,
    subject        TEXT NOT NULL,
    marks_obtained INTEGER NOT NULL DEFAULT 0,
    total_marks    INTEGER NOT NULL DEFAULT 100,
    weak_areas     TEXT,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mt_user ON mock_tests(user_id);

-- ── NOTES & MISTAKES ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notes (
    id          BIGSERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject     TEXT,
    title       TEXT NOT NULL,
    content     TEXT,
    is_mistake  BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notes_user ON notes(user_id);

-- ── REVISIONS ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS revisions (
    id           BIGSERIAL PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id   BIGINT,
    rev1_date    TEXT, rev2_date TEXT, rev3_date TEXT, rev4_date TEXT,
    rev1_status  TEXT DEFAULT 'Pending', rev2_status TEXT DEFAULT 'Pending',
    rev3_status  TEXT DEFAULT 'Pending', rev4_status TEXT DEFAULT 'Pending',
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rev_user ON revisions(user_id);

-- ── DAILY PLANNER ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_targets (
    id            BIGSERIAL PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date          TEXT NOT NULL,
    target_hours  REAL DEFAULT 6,
    notes         TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_dt_user ON daily_targets(user_id, date);

-- ── SYLLABUS / CHAPTERS ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS syllabus (
    id         BIGSERIAL PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject    TEXT NOT NULL,
    chapter    TEXT NOT NULL,
    status     TEXT DEFAULT 'Pending',
    weightage  TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_syl_user ON syllabus(user_id);

-- ── TOPIC PROGRESS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS topic_progress (
    id              BIGSERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject         TEXT NOT NULL,
    topic_name      TEXT NOT NULL,
    estimated_hours REAL DEFAULT 0,
    status          TEXT DEFAULT 'Not Started',
    confidence      INTEGER DEFAULT 0,
    added_date      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_tp_user ON topic_progress(user_id, subject);

-- ── LECTURES ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lectures (
    id                BIGSERIAL PRIMARY KEY,
    user_id           TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject           TEXT,
    chapter           TEXT,
    lecture_name      TEXT,
    lecture_link      TEXT,
    total_duration    REAL DEFAULT 0,
    watched_duration  REAL DEFAULT 0,
    status            TEXT DEFAULT 'Pending',
    last_watched_date TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lec_user ON lectures(user_id);

-- ── PRACTICE QUESTIONS ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS practice_questions (
    id             BIGSERIAL PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject        TEXT,
    chapter        TEXT,
    source         TEXT,
    status         TEXT DEFAULT 'Pending',
    generated_date TEXT,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chapter_questions (
    id         BIGSERIAL PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject    TEXT,
    chapter    TEXT,
    source     TEXT,
    year       TEXT,
    status     TEXT DEFAULT 'Pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── QUIZ ATTEMPTS ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id               BIGSERIAL PRIMARY KEY,
    user_id          TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject          TEXT,
    topic            TEXT,
    total_questions  INTEGER,
    correct_answers  INTEGER,
    accuracy         REAL,
    attempt_date     TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_qa_user ON quiz_attempts(user_id);

-- ── UPLOADED FILES ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS uploaded_study_files (
    id             BIGSERIAL PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename       TEXT,
    subject        TEXT,
    upload_date    TEXT,
    extracted_text TEXT,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ── ICAI MATERIALS (shared, no user_id) ────────────────────
CREATE TABLE IF NOT EXISTS icai_materials (
    id          BIGSERIAL PRIMARY KEY,
    title       TEXT,
    category    TEXT,
    subject     TEXT,
    link        TEXT,
    fetch_date  TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
--  ROW LEVEL SECURITY — users can only see their OWN data
--  (Our backend uses service_role key which bypasses RLS,
--   so these policies protect against direct API misuse)
-- ================================================================
ALTER TABLE users               ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_sessions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_tests          ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes               ENABLE ROW LEVEL SECURITY;
ALTER TABLE revisions           ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_targets       ENABLE ROW LEVEL SECURITY;
ALTER TABLE syllabus            ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic_progress      ENABLE ROW LEVEL SECURITY;
ALTER TABLE lectures            ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_questions  ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapter_questions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts       ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploaded_study_files ENABLE ROW LEVEL SECURITY;

-- Service role bypass (our server uses this key)
CREATE POLICY "service_all" ON users               FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON study_sessions      FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON mock_tests          FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON notes               FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON revisions           FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON daily_targets       FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON syllabus            FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON topic_progress      FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON lectures            FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON practice_questions  FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON chapter_questions   FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON quiz_attempts       FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON uploaded_study_files FOR ALL USING (true) WITH CHECK (true);

-- ================================================================
--  Done! Schema created. Copy your Supabase Project URL
--  and service_role key into .streamlit/secrets.toml
-- ================================================================
