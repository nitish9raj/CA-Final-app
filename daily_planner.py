import streamlit as st
from theme import get_theme
import database as db
from datetime import datetime, date
import pandas as pd

SUBJECTS = ["FR","AFM","Audit","DT","IDT","IBS"]
SC = {"FR":"#a78bfa","AFM":"#60a5fa","Audit":"#34d399","DT":"#fbbf24","IDT":"#f87171","IBS":"#38bdf8"}

def render_daily_planner():
    t = get_theme()
    D = t["dark"]

    st.markdown(f"""
    <div style="margin-bottom:24px;">
      <div style="font-size:26px;font-weight:800;color:{t['text']};letter-spacing:-0.04em;">
        🎯 Daily Planner</div>
      <div style="font-size:13px;color:{t['text2']};margin-top:4px;">
        Set daily targets and get smart auto-recommendations</div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📅  Today's Plan","🤖  Smart Auto-Planner","📋  History"])

    with tabs[0]:
        today_str = str(date.today())
        existing = db.fetch_data("SELECT * FROM daily_targets WHERE date=?", (today_str,))

        col_plan, col_prog = st.columns([1,1])
        with col_plan:
            with st.container(border=True):
                __text = t["text"]
                st.markdown(f"<div style='font-size:15px;font-weight:700;color:{__text};margin-bottom:14px;'>📅 Plan for {date.today().strftime('%A, %d %B %Y')}</div>", unsafe_allow_html=True)
                target_h = st.slider("Target Study Hours", 2.0, 16.0,
                    float(existing["target_hours"].iloc[0]) if not existing.empty and "target_hours" in existing.columns else 8.0, 0.5)
                focus_subjects = st.multiselect("Focus Subjects", SUBJECTS, default=SUBJECTS[:2], key="plan_subs")
                notes = st.text_area("Today's Goals",
                    value=existing["notes"].iloc[0] if not existing.empty and "notes" in existing.columns and pd.notna(existing["notes"].iloc[0]) else "",
                    placeholder="e.g. Complete Ind AS 115 + DT revision chapters 3-5", height=80, key="plan_notes")
                if st.button("💾 Save Plan", type="primary", use_container_width=True):
                    focus_str = ",".join(focus_subjects)
                    if not existing.empty:
                        db.execute_query("UPDATE daily_targets SET target_hours=?,notes=? WHERE date=?", (target_h, notes, today_str))
                    else:
                        db.execute_query("INSERT INTO daily_targets (date,target_hours,notes) VALUES (?,?,?)", (today_str, target_h, notes))
                    st.success("✅ Plan saved!")

        with col_prog:
            df_t = db.fetch_data("SELECT duration_minutes,subject FROM study_sessions WHERE date=?", (today_str,))
            actual_m = int(df_t["duration_minutes"].sum()) if not df_t.empty else 0
            actual_h = actual_m / 60
            tgt = target_h if target_h else 8.0
            pct = min(actual_h / tgt, 1.0)
            bar_col = "#34d399" if pct >= 1 else "#fbbf24" if pct >= 0.6 else t["accent"]

            st.markdown(f"""
            <div style="background:{t['card']};border:1px solid {t['border']};
                 border-radius:16px;padding:28px 24px;text-align:center;">
              <div style="font-size:10px;color:{t['text3']};text-transform:uppercase;
                   letter-spacing:2px;margin-bottom:10px;font-weight:700;">TODAY'S PROGRESS</div>
              <div style="font-size:44px;font-weight:800;color:{bar_col};
                   font-family:'SF Mono','JetBrains Mono',monospace;letter-spacing:-0.05em;
                   line-height:1;">{actual_h:.1f}h</div>
              <div style="font-size:13px;color:{t['text2']};margin:8px 0 18px;">
                of {tgt}h target</div>
              <div style="height:8px;background:{t['bg3']};border-radius:999px;overflow:hidden;margin-bottom:10px;">
                <div style="height:100%;width:{int(pct*100)}%;background:{bar_col};
                     border-radius:999px;"></div>
              </div>
              <div style="font-size:12px;color:{t['text2']};">
                {int(pct*100)}% complete — {max(0, tgt-actual_h):.1f}h remaining</div>
            </div>""", unsafe_allow_html=True)

            if pct >= 1.0:
                st.balloons()
                st.success("🏆 Daily target achieved!")

            if not df_t.empty:
                __text = t["text"]
                st.markdown(f"<div style='margin-top:16px;font-size:13px;font-weight:600;color:{__text};margin-bottom:8px;'>Sessions today:</div>", unsafe_allow_html=True)
                for s in df_t["subject"].unique():
                    m   = int(df_t[df_t["subject"] == s]["duration_minutes"].sum())
                    sc  = SC.get(str(s), t["accent"])
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                         padding:8px 0;border-bottom:1px solid {t['border']};">
                      <span style="color:{sc};font-weight:700;font-size:12px;">{s}</span>
                      <span style="color:{t['text2']};font-size:12px;">{m}m ({m/60:.1f}h)</span>
                    </div>""", unsafe_allow_html=True)

    with tabs[1]:
        __text = t["text"]
        st.markdown(f"<div style='font-size:15px;font-weight:700;color:{__text};margin-bottom:14px;'>🤖 Smart Study Planner</div>", unsafe_allow_html=True)
        exam_str = st.session_state.get("exam_date","2026-05-01")
        try: days_left = max(1,(datetime.strptime(exam_str,"%Y-%m-%d")-datetime.now()).days)
        except: days_left = 100

        daily_target_h = st.number_input("Your daily study target (hours)", 4.0, 16.0, 8.0, 0.5, key="smart_target")
        total_available = days_left * daily_target_h
        df_pending = db.fetch_data("SELECT subject, COUNT(*) as cnt FROM syllabus WHERE status='Pending' GROUP BY subject")

        st.markdown(f"""
        <div style="background:{"linear-gradient(135deg,#1e1b4b,#312e81)" if D else "linear-gradient(135deg,#ede9fe,#ddd6fe)"};
             border:1px solid {"rgba(124,111,247,0.4)" if D else "rgba(91,80,232,0.3)"};
             border-radius:16px;padding:22px;margin:16px 0;">
          <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:16px;">
            <div style="text-align:center;">
              <div style="font-size:30px;font-weight:800;color:{"#a5b4fc" if D else "#5b50e8"};
                   font-family:'SF Mono','JetBrains Mono',monospace;">{days_left}</div>
              <div style="font-size:11px;color:{t['text2']};font-weight:600;">Days Left</div>
            </div>
            <div style="text-align:center;">
              <div style="font-size:30px;font-weight:800;color:{"#a5b4fc" if D else "#5b50e8"};
                   font-family:'SF Mono','JetBrains Mono',monospace;">{int(total_available)}h</div>
              <div style="font-size:11px;color:{t['text2']};font-weight:600;">Total Hrs Available</div>
            </div>
            <div style="text-align:center;">
              <div style="font-size:30px;font-weight:800;color:{"#a5b4fc" if D else "#5b50e8"};
                   font-family:'SF Mono','JetBrains Mono',monospace;">
                {int(df_pending['cnt'].sum()) if not df_pending.empty else 0}</div>
              <div style="font-size:11px;color:{t['text2']};font-weight:600;">Chapters Pending</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        if df_pending.empty:
            st.success("🎉 All chapters completed! Focus on revision and mock tests.")
        else:
            total_pending = int(df_pending["cnt"].sum())
            hrs_per_ch = total_available / total_pending if total_pending > 0 else 0
            __text = t["text"]
            st.markdown(f"<div style='font-size:14px;font-weight:700;color:{__text};margin-bottom:12px;'>📋 Recommended Daily Allocation per Subject:</div>", unsafe_allow_html=True)
            for _, row in df_pending.iterrows():
                share   = row["cnt"] / total_pending if total_pending > 0 else 0
                daily_h = share * daily_target_h
                sc      = SC.get(str(row["subject"]), t["accent"])
                st.markdown(f"""
                <div style="margin-bottom:10px;padding:14px;background:{t['card']};
                     border:1px solid {t['border']};border-left:3px solid {sc};border-radius:12px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                      <span style="color:{sc};font-weight:700;">{row['subject']}</span>
                      <span style="color:{t['text2']};font-size:12px;margin-left:8px;">
                        {row['cnt']} chapters pending</span>
                    </div>
                    <div style="text-align:right;">
                      <div style="color:{t['text']};font-weight:700;">{daily_h:.1f}h/day</div>
                      <div style="color:{t['text2']};font-size:11px;">≈ {hrs_per_ch:.1f}h per chapter</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

    with tabs[2]:
        df_h = db.fetch_data("SELECT date,target_hours,notes FROM daily_targets ORDER BY date DESC LIMIT 30")
        if df_h.empty:
            st.info("No planner history yet.")
        else:
            for _, row in df_h.iterrows():
                df_actual = db.fetch_data("SELECT SUM(duration_minutes) as m FROM study_sessions WHERE date=?", (row["date"],))
                actual_m2 = int(df_actual["m"].iloc[0]) if not df_actual.empty and pd.notna(df_actual["m"].iloc[0]) else 0
                actual_h2 = actual_m2 / 60
                tgt2 = float(row["target_hours"]) if row["target_hours"] else 0
                pct2 = min(actual_h2 / tgt2, 1.0) if tgt2 > 0 else 0
                col2 = "#34d399" if pct2 >= 1 else "#fbbf24" if pct2 >= 0.6 else "#f87171"
                __text2 = t["text2"]
                note_html = f'<div style="font-size:11px;color:{__text2};margin-top:2px;">{str(row["notes"])[:60]}</div>' if row["notes"] and len(str(row["notes"])) > 0 else ""
                st.markdown(f"""
                <div style="margin-bottom:8px;padding:12px 16px;background:{t['card']};
                     border:1px solid {t['border']};border-radius:12px;
                     display:flex;justify-content:space-between;align-items:center;">
                  <div>
                    <span style="font-size:13px;font-weight:600;color:{t['text']};">{row['date']}</span>
                    {note_html}
                  </div>
                  <div style="text-align:right;">
                    <span style="color:{col2};font-weight:700;">{actual_h2:.1f}h / {tgt2}h</span>
                    <div style="font-size:11px;color:{t['text2']};">{int(pct2*100)}%</div>
                  </div>
                </div>""", unsafe_allow_html=True)
