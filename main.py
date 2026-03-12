"""
main.py — CA Final AI Suite v7.0 Cloud Edition
Firebase Auth  +  Supabase PostgreSQL  +  Streamlit
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime
import database as db
import auth

st.set_page_config(page_title="CA Final AI Suite", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")

# ── Default session state ────────────────────────────────────
if "theme"     not in st.session_state: st.session_state["theme"]     = "dark"
if "exam_date" not in st.session_state: st.session_state["exam_date"] = "2026-05-01"

# ════════════════════════════════════════════════════════════
#  AUTH GATE — show login page until signed in
# ════════════════════════════════════════════════════════════
if not auth.is_logged_in():
    auth.render_login_page()
    st.stop()

# ── Sync exam_date from user record once per session ─────────
user = auth.get_user()
if not st.session_state.get("exam_date_synced"):
    try:
        from supabase import create_client
        sb  = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        row = sb.table("users").select("exam_date").eq("id", user["uid"]).execute()
        if row.data and row.data[0].get("exam_date"):
            st.session_state["exam_date"] = row.data[0]["exam_date"]
    except Exception:
        pass
    st.session_state["exam_date_synced"] = True

D = st.session_state["theme"] == "dark"

# ── Design tokens ─────────────────────────────────────────────
if D:
    BG="#080c14"; BG2="#0d1117"; BG3="#0f1923"; CARD="#0d1117"
    BORDER="rgba(255,255,255,0.07)"; BORDER2="rgba(255,255,255,0.12)"
    TEXT="#e8eaf0"; TEXT2="#6b7280"; TEXT3="#374151"
    ACCENT="#00f5c4"; ACCENT2="#7b68ee"; ACCENT3="#f5a623"; ACCENT4="#ff6b9d"; ACCENT5="#56ccf2"
    SIDEBAR="#080c14"; INPUT="#0d1117"; SHADOW="rgba(0,0,0,0.7)"
    NHOV="rgba(0,245,196,0.06)"; NACT="rgba(0,245,196,0.10)"; SCR="rgba(255,255,255,0.12)"
    NAV_BORDER="rgba(0,245,196,0.30)"; NAV_TEXT=ACCENT
    S_BG="#041a10"; S_BD="#00f5c4"; S_TX="#00f5c4"
    I_BG="#06111e"; I_BD="#56ccf2"; I_TX="#56ccf2"
    W_BG="#1a1200"; W_BD="#f5a623"; W_TX="#f5a623"
    E_BG="#1a0610"; E_BD="#ff6b9d"; E_TX="#ff6b9d"
    GRAD="linear-gradient(135deg,#00f5c4,#7b68ee)"
    GLOW="0 0 24px rgba(0,245,196,0.15)"
else:
    BG="#f0f4f8"; BG2="#ffffff"; BG3="#e8edf5"; CARD="#ffffff"
    BORDER="rgba(0,0,0,0.14)"; BORDER2="rgba(0,0,0,0.22)"
    TEXT="#0d1117"; TEXT2="#4b5563"; TEXT3="#9ca3af"
    ACCENT="#00b894"; ACCENT2="#6c5ce7"; ACCENT3="#e17055"; ACCENT4="#e84393"; ACCENT5="#0984e3"
    SIDEBAR="#ffffff"; INPUT="#f0f4f8"; SHADOW="rgba(0,0,0,0.08)"
    NHOV="rgba(0,184,148,0.07)"; NACT="rgba(0,184,148,0.12)"; SCR="rgba(0,0,0,0.15)"
    NAV_BORDER="rgba(0,184,148,0.3)"; NAV_TEXT=ACCENT
    S_BG="#edfdf8"; S_BD="#00b894"; S_TX="#00785e"
    I_BG="#eaf6ff"; I_BD="#0984e3"; I_TX="#065a9e"
    W_BG="#fff8ee"; W_BD="#e17055"; W_TX="#9a3f1e"
    E_BG="#fff0f5"; E_BD="#e84393"; E_TX="#8b0052"
    GRAD="linear-gradient(135deg,#00b894,#6c5ce7)"
    GLOW="0 0 24px rgba(0,184,148,0.12)"

# ── Global CSS (identical to v6, preserved exactly) ──────────
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=JetBrains+Mono:wght@400;600;700&display=swap');

#MainMenu,footer,.stDeployButton,div[data-testid="stDecoration"],
[data-testid="stToolbar"],[data-testid="stStatusWidget"],
[data-testid="stHeader"],header[data-testid="stHeader"]
{{visibility:hidden!important;height:0!important;overflow:hidden!important;
  display:none!important;min-height:0!important;padding:0!important;margin:0!important;}}
.stApp > header, [data-testid="stAppViewContainer"] > header
{{display:none!important;height:0!important;min-height:0!important;}}

*,*::before,*::after{{box-sizing:border-box!important;}}
html,body,.stApp,[class*="css"]{{
  font-family:'DM Sans','Helvetica Neue',sans-serif!important;
  background:{BG}!important; color:{TEXT}!important;
  -webkit-font-smoothing:antialiased!important;}}
.main .block-container{{padding:24px 40px 64px!important;max-width:100%!important;background:{BG}!important;}}

[data-testid="stSidebar"]{{
  display:flex!important;visibility:visible!important;opacity:1!important;
  transform:translateX(0)!important;pointer-events:all!important;
  min-width:256px!important;max-width:256px!important;
  background:{SIDEBAR}!important;border-right:1px solid {BORDER}!important;z-index:100!important;}}
[data-testid="stSidebarCollapsedControl"]{{
  display:flex!important;visibility:visible!important;z-index:101!important;
  background:{ACCENT}!important;border-radius:0 12px 12px 0!important;}}
[data-testid="stSidebarCollapsedControl"] button{{background:{ACCENT}!important;color:#000!important;border:none!important;}}

[data-testid="stSidebar"] .stRadio>label{{display:none!important;}}
[data-testid="stSidebar"] .stRadio>div{{display:flex!important;flex-direction:column!important;gap:1px!important;padding:0 8px!important;}}
[data-testid="stSidebar"] .stRadio>div>label{{
  display:flex!important;align-items:center!important;padding:9px 12px!important;
  border-radius:10px!important;cursor:pointer!important;border:1px solid transparent!important;
  margin:0!important;line-height:1.4!important;color:{TEXT2}!important;font-size:13px!important;
  font-weight:500!important;transition:background .12s,color .12s!important;white-space:nowrap!important;}}
[data-testid="stSidebar"] .stRadio>div>label:hover{{background:{NHOV}!important;color:{TEXT}!important;}}
[data-testid="stSidebar"] .stRadio>div>label:has(input:checked){{
  background:{NACT}!important;color:{NAV_TEXT}!important;
  border-color:{NAV_BORDER}!important;font-weight:700!important;}}
[data-testid="stSidebar"] .stRadio>div>label>div:first-child{{display:none!important;width:0!important;height:0!important;overflow:hidden!important;}}
[data-testid="stSidebar"] .stRadio>div>label>div:last-child,
[data-testid="stSidebar"] .stRadio>div>label>div:nth-child(2){{display:block!important;visibility:visible!important;color:inherit!important;font-size:inherit!important;font-weight:inherit!important;opacity:1!important;}}
[data-testid="stSidebar"] .stRadio>div>label p{{display:inline!important;visibility:visible!important;color:inherit!important;font-size:13px!important;font-weight:inherit!important;margin:0!important;}}
[data-testid="stSidebar"] .stRadio>div>label:nth-child(7)::before{{content:"PHASE 2";display:block;font-size:9px;font-weight:700;color:{TEXT3};text-transform:uppercase;letter-spacing:2.5px;padding:14px 2px 6px;}}
[data-testid="stSidebar"] .stRadio>div>label:nth-child(10)::before{{content:"AI FEATURES";display:block;font-size:9px;font-weight:700;color:{TEXT3};text-transform:uppercase;letter-spacing:2.5px;padding:14px 2px 6px;}}
[data-testid="stSidebar"] .stRadio>div>label:nth-child(13)::before{{content:"OTHER";display:block;font-size:9px;font-weight:700;color:{TEXT3};text-transform:uppercase;letter-spacing:2.5px;padding:14px 2px 6px;}}

[data-testid="stVerticalBlockBorderWrapper"]>div{{
  background:{CARD}!important;border:1.5px solid {BORDER2}!important;
  border-radius:18px!important;box-shadow:0 2px 16px {SHADOW}!important;}}
[data-testid="stVerticalBlockBorderWrapper"]>div:hover{{box-shadow:{GLOW},0 8px 32px {SHADOW}!important;}}

[data-testid="metric-container"]{{background:{CARD}!important;border:1px solid {BORDER}!important;
  border-radius:16px!important;padding:20px!important;box-shadow:0 2px 10px {SHADOW}!important;transition:transform .18s,box-shadow .18s!important;}}
[data-testid="metric-container"]:hover{{transform:translateY(-3px)!important;box-shadow:{GLOW}!important;}}
[data-testid="stMetricValue"]{{font-size:1.9rem!important;font-weight:800!important;color:{TEXT}!important;font-family:'JetBrains Mono',monospace!important;letter-spacing:-0.05em!important;}}
[data-testid="stMetricLabel"]{{color:{TEXT2}!important;font-size:10px!important;text-transform:uppercase!important;letter-spacing:2px!important;font-weight:700!important;}}

.stButton>button{{border-radius:10px!important;font-weight:600!important;font-size:13px!important;
  transition:all .14s ease!important;border:1px solid {BORDER2}!important;color:{TEXT2}!important;
  background:{CARD}!important;letter-spacing:-0.01em!important;padding:8px 18px!important;font-family:'DM Sans',sans-serif!important;}}
.stButton>button:hover{{border-color:{ACCENT}!important;color:{ACCENT}!important;background:{NACT}!important;transform:translateY(-1px)!important;}}
.stButton>button[kind="primary"]{{background:{GRAD}!important;border:none!important;color:#000!important;font-weight:700!important;box-shadow:0 3px 14px rgba(0,245,196,.3)!important;}}
.stButton>button[kind="primary"]:hover{{filter:brightness(1.08)!important;transform:translateY(-1px)!important;color:#000!important;}}

.stTabs [data-baseweb="tab-list"]{{gap:3px!important;background:transparent!important;border-bottom:1px solid {BORDER}!important;}}
.stTabs [data-baseweb="tab"]{{border-radius:10px 10px 0 0!important;padding:8px 18px!important;background:transparent!important;border:1px solid transparent!important;color:{TEXT2}!important;font-weight:500!important;font-size:13px!important;transition:all .12s!important;}}
.stTabs [data-baseweb="tab"]:hover{{color:{TEXT}!important;background:{NHOV}!important;}}
.stTabs [aria-selected="true"]{{background:{NACT}!important;color:{ACCENT}!important;border-color:{NAV_BORDER}!important;border-bottom-color:{BG}!important;font-weight:700!important;}}

.stTextInput>div>div>input,.stNumberInput>div>div>input,.stDateInput>div>div>input,.stTextArea>div>div>textarea{{
  background:{INPUT}!important;border:1px solid {BORDER2}!important;border-radius:10px!important;color:{TEXT}!important;font-size:13px!important;font-family:'DM Sans',sans-serif!important;}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{{border-color:{ACCENT}!important;box-shadow:0 0 0 3px rgba(0,245,196,0.15)!important;outline:none!important;}}
[data-baseweb="select"]>div{{background:{INPUT}!important;border:1px solid {BORDER2}!important;border-radius:10px!important;color:{TEXT}!important;}}
[data-baseweb="popover"]{{background:{CARD}!important;border:1px solid {BORDER2}!important;border-radius:14px!important;box-shadow:0 16px 48px {SHADOW}!important;}}
[data-baseweb="option"]{{background:{CARD}!important;color:{TEXT}!important;}}
[data-baseweb="option"]:hover{{background:{NHOV}!important;}}
[data-baseweb="select"] span,[data-baseweb="select"] div{{color:{TEXT}!important;}}
[data-baseweb="select"] svg{{fill:{TEXT2}!important;}}

.stProgress>div>div>div{{background:{GRAD}!important;border-radius:999px!important;}}
.stProgress>div>div{{background:{BG3}!important;border-radius:999px!important;height:6px!important;}}

.stSuccess{{background:{S_BG}!important;border:1px solid {S_BD}!important;border-radius:10px!important;color:{S_TX}!important;}}
.stInfo{{background:{I_BG}!important;border:1px solid {I_BD}!important;border-radius:10px!important;color:{I_TX}!important;}}
.stWarning{{background:{W_BG}!important;border:1px solid {W_BD}!important;border-radius:10px!important;color:{W_TX}!important;}}
.stError{{background:{E_BG}!important;border:1px solid {E_BD}!important;border-radius:10px!important;color:{E_TX}!important;}}

.stNumberInput>div>div>input{{background:{INPUT}!important;color:{TEXT}!important;border:1px solid {BORDER2}!important;border-radius:10px!important;font-size:14px!important;font-weight:600!important;}}
.stNumberInput>div>div>button{{background:{BG3}!important;color:{TEXT}!important;border:1px solid {BORDER}!important;}}
.stNumberInput>div>div>button:hover{{background:{NACT}!important;color:{ACCENT}!important;}}

label,.stTextInput label,.stTextArea label,.stSelectbox label,[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] span{{color:{TEXT2}!important;font-size:13px!important;font-weight:500!important;}}
[data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3,[data-testid="stMarkdownContainer"] strong{{color:{TEXT}!important;}}
[data-testid="stMarkdownContainer"] p{{color:{TEXT2}!important;}}
.stTextArea textarea{{color:{TEXT}!important;caret-color:{ACCENT}!important;}}
.stTextInput input{{color:{TEXT}!important;caret-color:{ACCENT}!important;}}
input::placeholder,textarea::placeholder{{color:{TEXT3}!important;opacity:0.7!important;}}

[data-testid="stFileUploader"]{{background:{INPUT}!important;border:1.5px dashed {BORDER2}!important;border-radius:12px!important;}}
[data-testid="stFileUploader"]:hover{{border-color:{ACCENT}!important;}}
[data-testid="stExpander"]{{background:{CARD}!important;border:1px solid {BORDER}!important;border-radius:12px!important;}}
details summary{{color:{TEXT2}!important;font-weight:600!important;font-size:13px!important;}}
[data-testid="stDataFrame"]{{border:1px solid {BORDER}!important;border-radius:12px!important;overflow:hidden!important;}}
hr{{border-color:{BORDER}!important;margin:24px 0!important;}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:{SCR};border-radius:999px;}}
.stSlider>div>div>div{{background:{ACCENT}!important;}}
[data-baseweb="tag"]{{background:{NACT}!important;color:{ACCENT}!important;border-radius:6px!important;}}
.accent-card{{border-left:3px solid {ACCENT}!important;}}
</style>""", unsafe_allow_html=True)

db.init_db()

MENU_ITEMS = [
    "🏠  Dashboard","⏱️  Study Tracker","📚  Syllabus & Revisions",
    "🔁  Revision Schedule","📉  Tests & Analytics","🎯  Daily Planner",
    "▶️  Lecture Library","📝  Practice Questions","📋  Exam Mapping",
    "🧠  AI Insights","📄  AI File Analyzer","🏛️  ICAI Library","⚙️  Settings",
]

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    hcol, tcol = st.columns([5, 1])
    with hcol:
        st.markdown(f"""
        <div style="padding:18px 4px 8px;">
          <div style="font-size:9px;letter-spacing:3.5px;color:{ACCENT};font-weight:700;
               text-transform:uppercase;margin-bottom:4px;">CA FINAL</div>
          <div style="font-size:21px;font-weight:800;letter-spacing:-0.06em;line-height:1.15;
               background:{GRAD};-webkit-background-clip:text;
               -webkit-text-fill-color:transparent;background-clip:text;">AI Suite ☁️</div>
          <div style="font-size:10px;color:{TEXT3};margin-top:4px;
               font-family:'JetBrains Mono',monospace;">v7.0 · Cloud Edition</div>
        </div>""", unsafe_allow_html=True)
    with tcol:
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        if st.button("☀️" if D else "🌙", key="thm", help="Toggle theme"):
            st.session_state["theme"] = "light" if D else "dark"
            st.rerun()

    # ── User profile chip ─────────────────────────────────────
    prov_icon = {"google":"🔗","phone":"📱","email":"✉️"}.get(user["provider"], "👤")
    display_name = user["name"] or user["email"].split("@")[0] if user["email"] else "User"
    st.markdown(f"""
    <div style="margin:2px 8px 12px;padding:10px 12px;
         background:{'rgba(0,245,196,0.05)' if D else 'rgba(0,184,148,0.06)'};
         border:1px solid {'rgba(0,245,196,0.18)' if D else 'rgba(0,184,148,0.2)'};
         border-radius:12px;display:flex;align-items:center;gap:10px;">
      <div style="font-size:28px;line-height:1;">👤</div>
      <div style="flex:1;min-width:0;">
        <div style="font-size:13px;font-weight:700;color:{TEXT};
             white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{display_name}</div>
        <div style="font-size:10px;color:{TEXT3};margin-top:1px;">
          {prov_icon} {user['provider'].title()} · Free plan</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Exam countdown ────────────────────────────────────────
    try:
        days_left = max(0,(datetime.strptime(st.session_state["exam_date"],"%Y-%m-%d")-datetime.now()).days)
    except:
        days_left = 0
    clr = "#ff6b9d" if days_left<30 else "#f5a623" if days_left<60 else ACCENT
    pct = min(100, int((1-days_left/365)*100))
    st.markdown(f"""
    <div style="margin:0 8px 14px;
         background:{'rgba(0,245,196,0.05)' if D else 'rgba(0,184,148,0.06)'};
         border:1px solid {'rgba(0,245,196,0.18)' if D else 'rgba(0,184,148,0.2)'};
         border-radius:14px;padding:13px 16px;">
      <div style="font-size:9px;color:{TEXT3};text-transform:uppercase;
           letter-spacing:2.5px;margin-bottom:3px;font-weight:700;">EXAM IN</div>
      <div style="font-size:34px;font-weight:800;color:{clr};line-height:1;
           font-family:'JetBrains Mono',monospace;letter-spacing:-0.05em;">{days_left}</div>
      <div style="font-size:11px;color:{TEXT2};margin:4px 0 10px;font-weight:500;">days remaining</div>
      <div style="height:3px;background:{'rgba(255,255,255,0.07)' if D else 'rgba(0,0,0,0.07)'};border-radius:999px;">
        <div style="height:100%;width:{pct}%;background:{clr};border-radius:999px;"></div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding:0 12px 7px;font-size:9px;color:{TEXT3};
         text-transform:uppercase;letter-spacing:2.5px;font-weight:700;">NAVIGATION</div>""",
    unsafe_allow_html=True)

    choice = st.radio("nav", MENU_ITEMS, label_visibility="collapsed", key="nav_radio")

    # ── Stats chips ───────────────────────────────────────────
    ns = db.count_rows("study_sessions")
    nc = db.count_rows("syllabus", {"status": "Completed"})
    nl = db.count_rows("lectures", {"status": "Completed"})
    nq = db.count_rows("quiz_attempts")
    cells = ""
    for v, c, l in [(ns,ACCENT,"sessions"),(nc,ACCENT2,"chapters"),(nl,ACCENT4,"lectures"),(nq,ACCENT3,"quizzes")]:
        cells += f"""<div style="background:{'rgba(255,255,255,0.03)' if D else 'rgba(0,0,0,0.03)'};
          border:1px solid {('rgba(255,255,255,0.07)' if D else 'rgba(0,0,0,0.07)')};
          border-radius:10px;padding:9px 6px;text-align:center;">
          <div style="font-size:17px;font-weight:700;color:{c};
               font-family:'JetBrains Mono',monospace;letter-spacing:-0.03em;">{v}</div>
          <div style="font-size:9px;color:{TEXT3};text-transform:uppercase;
               letter-spacing:1.2px;margin-top:2px;font-weight:600;">{l}</div></div>"""
    st.markdown(f"""
    <div style="margin:14px 8px 10px;padding-top:14px;border-top:1px solid {BORDER};">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;">{cells}</div>
    </div>""", unsafe_allow_html=True)

    # ── Sign Out ──────────────────────────────────────────────
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    if st.button("🚪  Sign Out", use_container_width=True, key="signout_btn"):
        auth.logout()

# ── Module routing ───────────────────────────────────────────
if   "Dashboard"         in choice: from modules.dashboard          import render_dashboard;          render_dashboard()
elif "Study Tracker"     in choice: from modules.study_tracker      import render_study_tracker;      render_study_tracker()
elif "Syllabus"          in choice: from modules.syllabus_tracker   import render_syllabus_tracker;   render_syllabus_tracker()
elif "Revision Schedule" in choice: from modules.revision_schedule  import render_revision_schedule;  render_revision_schedule()
elif "Tests"             in choice: from modules.tests_analytics    import render_tests_analytics;    render_tests_analytics()
elif "Daily Planner"     in choice: from modules.daily_planner      import render_daily_planner;      render_daily_planner()
elif "Lecture"           in choice: from modules.lecture_library    import render_lecture_library;    render_lecture_library()
elif "Practice"          in choice: from modules.practice_generator import render_practice_generator; render_practice_generator()
elif "Exam Mapping"      in choice: from modules.exam_mapping       import render_exam_mapping;       render_exam_mapping()
elif "AI Insights"       in choice: from modules.ai_insights        import render_ai_insights;        render_ai_insights()
elif "AI File"           in choice: from modules.ai_study_assistant import render_ai_study_assistant; render_ai_study_assistant()
elif "ICAI"              in choice: from modules.icai_library       import render_icai_library;       render_icai_library()
elif "Settings"          in choice:
    st.markdown(f"<div style='font-size:26px;font-weight:800;color:{TEXT};letter-spacing:-0.04em;margin-bottom:22px;'>⚙️ Settings</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:15px;font-weight:700;color:{TEXT};margin-bottom:12px;'>📅 Exam Date</div>", unsafe_allow_html=True)
            cur = datetime.strptime(st.session_state["exam_date"],"%Y-%m-%d").date()
            nd  = st.date_input("CA Final Exam Date", value=cur)
            if st.button("💾 Save Date", type="primary", use_container_width=True):
                st.session_state["exam_date"] = nd.strftime("%Y-%m-%d")
                try:
                    from supabase import create_client
                    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
                    sb.table("users").update({"exam_date": nd.strftime("%Y-%m-%d")}).eq("id", user["uid"]).execute()
                except: pass
                st.success("✅ Date saved to cloud!"); st.rerun()
    with c2:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:15px;font-weight:700;color:{TEXT};margin-bottom:12px;'>👤 Account</div>", unsafe_allow_html=True)
            prov_label = {"google":"Google","phone":"Phone OTP","email":"Email & Password"}.get(user["provider"],"Email")
            st.markdown(f"""
            <div style="font-size:13px;color:{TEXT2};line-height:2.2;">
              <b style="color:{TEXT};">Name:</b> {user['name']}<br>
              <b style="color:{TEXT};">Email:</b> {user['email'] or '—'}<br>
              <b style="color:{TEXT};">Login via:</b> {prov_label}<br>
              <b style="color:{TEXT};">Plan:</b> Free 🎉
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("🚪 Sign Out", type="primary", use_container_width=True, key="settings_signout"):
                auth.logout()
    st.divider()
    with st.container(border=True):
        st.markdown(f"<div style='font-size:14px;font-weight:700;color:{TEXT};margin-bottom:8px;'>📊 Your Data Summary</div>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("Study Sessions", db.count_rows("study_sessions"))
        dc2.metric("Mock Tests",     db.count_rows("mock_tests"))
        dc3.metric("Quiz Attempts",  db.count_rows("quiz_attempts"))
        dc4, dc5, dc6 = st.columns(3)
        dc4.metric("Chapters",  db.count_rows("syllabus"))
        dc5.metric("Lectures",  db.count_rows("lectures"))
        dc6.metric("Topics",    db.count_rows("topic_progress"))
    st.divider()
    with st.container(border=True):
        st.markdown(f"<div style='font-size:14px;font-weight:700;color:{TEXT};margin-bottom:8px;'>⚠️ Danger Zone</div>", unsafe_allow_html=True)
        st.warning("Permanently deletes ALL your study data — cannot be undone.")
        if st.checkbox("I understand, delete everything"):
            if st.button("🗑️ Delete All My Data", type="primary"):
                uid = user["uid"]
                try:
                    from supabase import create_client
                    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
                    for tbl in ["study_sessions","syllabus","revisions","mock_tests",
                                "daily_targets","lectures","practice_questions",
                                "chapter_questions","uploaded_study_files",
                                "quiz_attempts","topic_progress","notes"]:
                        sb.table(tbl).delete().eq("user_id", uid).execute()
                    db.fetch_data.clear()
                    st.success("All data cleared."); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
