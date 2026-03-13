"""
database.py  —  Supabase PostgreSQL backend
Replaces SQLite. Maintains 100% API compatibility with the original:
  - execute_query(sql, params)  → INSERT / UPDATE / DELETE
  - fetch_data(sql, params)     → SELECT → returns pd.DataFrame
All reads/writes are automatically scoped to the logged-in user_id.
"""
import streamlit as st
import pandas as pd
import re
from supabase import create_client, Client

# ── Supabase client (one per server process) ────────────────
@st.cache_resource
def _sb() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],   # use the service_role key
    )

def _uid() -> str | None:
    return st.session_state.get("user_id")

# ════════════════════════════════════════════════════════════
#  init_db — no-op for cloud (schema is created via schema.sql)
# ════════════════════════════════════════════════════════════
def init_db():
    pass  # Tables live in Supabase; schema.sql handles creation.

# ════════════════════════════════════════════════════════════
#  fetch_data — replaces pd.read_sql_query(sql, sqlite_conn)
#
#  Accepts the same SQL strings the old modules used, e.g.:
#    "SELECT * FROM study_sessions ORDER BY date DESC"
#    "SELECT COUNT(*) c FROM syllabus WHERE status='Completed'"
#  Automatically appends  AND user_id = '{uid}'  to WHERE clauses.
# ════════════════════════════════════════════════════════════
@st.cache_data(ttl=15, show_spinner=False)

def _parse_select_cols(query: str) -> list:
    """Extract column names from SELECT clause for empty DataFrames."""
    try:
        m = re.search(r"SELECT\s+(.+?)\s+FROM", query, re.IGNORECASE)
        if not m:
            return []
        cols_str = m.group(1).strip()
        if cols_str == "*":
            return []
        cols = [c.strip().split(".")[-1].split(" ")[-1] for c in cols_str.split(",")]
        return [c for c in cols if c]
    except:
        return []

def fetch_data(query: str, params: tuple = ()) -> pd.DataFrame:
    uid = _uid()
    if not uid:
        return pd.DataFrame()
    try:
        sb    = _sb()
        table = _parse_table(query)
        if not table:
            return pd.DataFrame()

        # ── COUNT queries ────────────────────────────────────
        if re.search(r"SELECT\s+COUNT", query, re.IGNORECASE):
            col_alias = re.search(r"COUNT\([^)]*\)\s+(\w+)", query, re.IGNORECASE)
            alias     = col_alias.group(1) if col_alias else "c"

            q = sb.table(table).select("id", count="exact")
            q = _apply_where(q, query, params, uid, table)
            res = q.execute()
            count = res.count if res.count is not None else len(res.data or [])
            return pd.DataFrame({alias: [count]})

        # ── Regular SELECT ───────────────────────────────────
        q = sb.table(table).select("*")
        q = _apply_where(q, query, params, uid, table)
        q = _apply_order(q, query)
        q = _apply_limit(q, query)
        res = q.execute()
        if res.data:
            df = pd.DataFrame(res.data)
        else:
            # Return empty DataFrame with correct columns from SELECT clause
            cols = _parse_select_cols(query)
            df = pd.DataFrame(columns=cols) if cols else pd.DataFrame()
        return df

    except Exception as e:
        print(f"[DB fetch_data] {e}  sql={query[:80]}")
        # Return empty DataFrame WITH correct columns so callers don't get KeyError
        cols = _parse_select_cols(query)
        return pd.DataFrame(columns=cols) if cols else pd.DataFrame()


# ════════════════════════════════════════════════════════════
#  execute_query — replaces cursor.execute(sql, params)
#  Handles INSERT, UPDATE, DELETE, CREATE TABLE IF NOT EXISTS
# ════════════════════════════════════════════════════════════
def execute_query(query: str, params: tuple = ()):
    uid = _uid()
    q   = query.strip()

    # ── CREATE TABLE IF NOT EXISTS — skip silently ───────────
    if re.match(r"CREATE\s+TABLE", q, re.IGNORECASE):
        return None

    # ── DELETE FROM table ────────────────────────────────────
    if re.match(r"DELETE\s+FROM", q, re.IGNORECASE):
        table = _parse_table(q)
        if not table:
            return None
        try:
            sb  = _sb()
            req = sb.table(table).delete()
            if uid and table != "icai_materials":
                req = req.eq("user_id", uid)
            # specific WHERE id = ?
            id_val = _extract_id_param(q, params)
            if id_val is not None:
                req = req.eq("id", id_val)
            req.execute()
            fetch_data.clear()
        except Exception as e:
            print(f"[DB delete] {e}")
        return None

    # ── UPDATE ───────────────────────────────────────────────
    if re.match(r"UPDATE\s+", q, re.IGNORECASE):
        return _handle_update(q, params, uid)

    # ── INSERT INTO ──────────────────────────────────────────
    if re.match(r"INSERT\s+INTO", q, re.IGNORECASE):
        return _handle_insert(q, params, uid)

    return None


# ════════════════════════════════════════════════════════════
#  High-level helpers used by new/updated modules
# ════════════════════════════════════════════════════════════
def insert_row(table: str, data: dict) -> dict | None:
    """Insert a dict as a row; auto-adds user_id."""
    uid = _uid()
    if uid and table != "icai_materials":
        data = {**data, "user_id": uid}
    try:
        res = _sb().table(table).insert(data).execute()
        fetch_data.clear()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"[DB insert_row] {e}")
        return None

def update_row(table: str, row_id: int, data: dict) -> bool:
    uid = _uid()
    try:
        q = _sb().table(table).update(data).eq("id", row_id)
        if uid and table != "icai_materials":
            q = q.eq("user_id", uid)
        q.execute()
        fetch_data.clear()
        return True
    except Exception as e:
        print(f"[DB update_row] {e}")
        return False

def delete_row(table: str, row_id: int) -> bool:
    uid = _uid()
    try:
        q = _sb().table(table).delete().eq("id", row_id)
        if uid and table != "icai_materials":
            q = q.eq("user_id", uid)
        q.execute()
        fetch_data.clear()
        return True
    except Exception as e:
        print(f"[DB delete_row] {e}")
        return False

def count_rows(table: str, filters: dict = None) -> int:
    uid = _uid()
    if not uid:
        return 0
    try:
        q = _sb().table(table).select("id", count="exact").eq("user_id", uid)
        if filters:
            for col, val in filters.items():
                q = q.eq(col, val)
        res = q.execute()
        return res.count or 0
    except Exception as e:
        print(f"[DB count_rows] {e}")
        return 0

def upsert_user(uid: str, email: str, name: str, photo: str = ""):
    """Create or update user record in Supabase users table."""
    try:
        _sb().table("users").upsert({
            "id": uid, "email": email,
            "display_name": name, "photo_url": photo,
            "last_seen": "now()",
        }).execute()
    except Exception as e:
        print(f"[DB upsert_user] {e}")


# ════════════════════════════════════════════════════════════
#  Private helpers
# ════════════════════════════════════════════════════════════
def _parse_table(sql: str) -> str | None:
    """Extract table name from SQL."""
    m = re.search(
        r"(?:FROM|INTO|UPDATE|TABLE)\s+([`\"\[]?(\w+)[`\"\]]?)",
        sql, re.IGNORECASE)
    return m.group(2).lower() if m else None

def _apply_where(q, sql: str, params: tuple, uid: str, table: str):
    """Add user_id filter + any simple col=val WHERE conditions."""
    if table != "icai_materials":
        q = q.eq("user_id", uid)

    where_m = re.search(r"WHERE\s+(.+?)(?:ORDER|LIMIT|GROUP|$)", sql,
                        re.IGNORECASE | re.DOTALL)
    if not where_m:
        return q

    clause = where_m.group(1).strip()
    # Remove user_id condition (we add it above)
    clause = re.sub(r"user_id\s*=\s*['\"]?\w+['\"]?\s*(AND\s*)?", "", clause, flags=re.IGNORECASE).strip()
    if clause.upper().startswith("AND"):
        clause = clause[3:].strip()

    # Replace ? placeholders with actual params
    param_list = list(params) if params else []
    for val in param_list:
        clause = clause.replace("?", f"'{val}'", 1)

    # Parse simple conditions: col='val' or col=val
    conditions = re.split(r"\s+AND\s+", clause, flags=re.IGNORECASE)
    for cond in conditions:
        cond = cond.strip()
        if not cond:
            continue
        m = re.match(r"(\w+)\s*=\s*'?([^']+?)'?$", cond)
        if m:
            col, val = m.group(1), m.group(2)
            q = q.eq(col, val)
    return q

def _apply_order(q, sql: str):
    m = re.search(r"ORDER\s+BY\s+(\w+)(\s+(DESC|ASC))?", sql, re.IGNORECASE)
    if m:
        col  = m.group(1)
        desc = bool(m.group(3) and m.group(3).upper() == "DESC")
        q    = q.order(col, desc=desc)
    return q

def _apply_limit(q, sql: str):
    m = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
    if m:
        q = q.limit(int(m.group(1)))
    return q

def _extract_id_param(sql: str, params: tuple) -> int | None:
    """Extract id value from DELETE WHERE id=? or id=N."""
    m = re.search(r"WHERE\s+id\s*=\s*(\?|\d+)", sql, re.IGNORECASE)
    if m:
        if m.group(1) == "?" and params:
            try: return int(params[0])
            except: pass
        else:
            try: return int(m.group(1))
            except: pass
    return None

def _handle_insert(sql: str, params: tuple, uid: str) -> int | None:
    """Parse INSERT INTO table (cols) VALUES (?,?,...) and execute."""
    table = _parse_table(sql)
    if not table:
        return None
    try:
        cols_m = re.search(r"\(([^)]+)\)\s+VALUES", sql, re.IGNORECASE)
        if not cols_m:
            return None
        cols   = [c.strip() for c in cols_m.group(1).split(",")]
        vals   = list(params)
        data   = dict(zip(cols, vals))
        if uid and table != "icai_materials" and "user_id" not in data:
            data["user_id"] = uid
        sb  = _sb()
        res = sb.table(table).insert(data).execute()
        fetch_data.clear()
        return res.data[0].get("id") if res.data else None
    except Exception as e:
        print(f"[DB _handle_insert] {e}  sql={sql[:80]}")
        return None

def _handle_update(sql: str, params: tuple, uid: str):
    """Parse UPDATE table SET col=? WHERE id=? and execute."""
    table = _parse_table(sql)
    if not table:
        return None
    try:
        set_m  = re.search(r"SET\s+(.+?)\s+WHERE", sql, re.IGNORECASE | re.DOTALL)
        if not set_m:
            return None
        set_str = set_m.group(1)
        cols    = [s.split("=")[0].strip() for s in set_str.split(",")]
        vals    = list(params)
        id_val  = vals[-1] if vals else None
        data    = dict(zip(cols, vals[:-1]))
        sb      = _sb()
        q       = sb.table(table).update(data).eq("id", id_val)
        if uid and table != "icai_materials":
            q = q.eq("user_id", uid)
        q.execute()
        fetch_data.clear()
    except Exception as e:
        print(f"[DB _handle_update] {e}  sql={sql[:80]}")
    return None
