import streamlit as st
from theme import get_theme
import database as db
from datetime import datetime, date
import pandas as pd
import plotly.graph_objects as go

SUBJECTS = ["FR","AFM","Audit","DT","IDT","IBS"]
SUBJECT_FULL = {
    "FR": "Financial Reporting",  "AFM": "Advanced Financial Mgmt",
    "Audit": "Advanced Auditing", "DT": "Direct Tax Laws",
    "IDT": "Indirect Tax Laws",   "IBS": "Integrated Business Solutions",
}
CATEGORIES = ["Self Study","Lectures","Revision","Practice","Mock Test"]
SUBJECT_COLORS = {
    "FR":"#00f5c4","AFM":"#7b68ee","Audit":"#f5a623",
    "DT":"#ff6b9d","IDT":"#56ccf2","IBS":"#a78bfa"
}
SUBJECT_ICONS = {"FR":"📊","AFM":"📈","Audit":"🔍","DT":"🧾","IDT":"🏛️","IBS":"💻"}

DEFAULT_TOPICS = {
    "FR":  [("Ind AS 115 – Revenue Recognition",12),("Ind AS 116 – Leases",8),
            ("Ind AS 36 – Impairment of Assets",6),("Consolidation & Group Accounts",15),
            ("Ind AS 109 – Financial Instruments",10),("Business Combinations Ind AS 103",8)],
    "AFM": [("Portfolio Management & CAPM",10),("Derivatives & Options Pricing",12),
            ("Foreign Exchange Risk Mgmt",8),("Mergers & Acquisitions",10),
            ("Interest Rate Risk Mgmt",7)],
    "Audit":[("SA 700 Series – Audit Reports",6),("Forensic Accounting",8),
             ("Internal Audit & Risk",7),("IT Audit Concepts",6),
             ("Standards on Auditing – Key SAs",10)],
    "DT":  [("Business Income & PGBP",12),("International Taxation & DTAA",15),
            ("Transfer Pricing",8),("Capital Gains",7),("Assessment Procedures",6)],
    "IDT": [("GST – Supply & ITC",12),("GST – Place of Supply",8),
            ("Customs Law",10),("GST Returns & Compliance",7)],
    "IBS": [("IS Audit & Controls",10),("ERP Systems",8),
            ("Information Security",6),("IT Governance",5)],
}

STATUS_COLORS = {"Completed":"#00f5c4","In Progress":"#f5a623","Not Started":"#374151"}
STATUS_ICONS  = {"Completed":"✅","In Progress":"🔄","Not Started":"⭕"}


def _ensure_topic_table():
    db.execute_query("""CREATE TABLE IF NOT EXISTS topic_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT, topic_name TEXT, estimated_hours REAL,
        status TEXT DEFAULT 'Not Started', confidence INTEGER DEFAULT 0,
        added_date TEXT)""")


def _load_topics(subject):
    _ensure_topic_table()
    df = db.fetch_data(
        "SELECT id,topic_name,estimated_hours,status,confidence FROM topic_progress WHERE subject=? ORDER BY id",
        (subject,))
    if df.empty:
        for name, hrs in DEFAULT_TOPICS.get(subject, []):
            db.execute_query(
                "INSERT INTO topic_progress (subject,topic_name,estimated_hours,status,confidence,added_date) VALUES (?,?,?,?,?,?)",
                (subject, name, hrs, "Not Started", 0, str(date.today())))
        df = db.fetch_data(
            "SELECT id,topic_name,estimated_hours,status,confidence FROM topic_progress WHERE subject=? ORDER BY id",
            (subject,))
    return df


def render_study_tracker():
    t = get_theme()
    D = t["dark"]
    accent  = t["accent"]
    accent2 = t["accent2"]
    accent3 = t["accent3"]
    accent4 = t["accent4"]
    accent5 = t["accent5"]

    st.markdown(f"""
    <div style="margin-bottom:28px;">
      <div style="font-size:28px;font-weight:800;color:{t['text']};letter-spacing:-0.05em;">
        ⏱️ Study Tracker</div>
      <div style="font-size:13px;color:{t['text2']};margin-top:4px;">
        Log sessions · Track topic progress · Pomodoro timer</div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📝  Log Session", "🍅  Pomodoro Timer",
                    "📋  History & Stats", "📚  Progress Tracker"])

    # ══════════════════════════════════════════════════════
    # TAB 0 – LOG SESSION
    # ══════════════════════════════════════════════════════
    with tabs[0]:
        col_form, col_recent = st.columns([1,1])

        with col_form:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:15px;font-weight:700;color:{t['text']};margin-bottom:14px;'>Log a Study Session</div>", unsafe_allow_html=True)
                subject  = st.selectbox("Subject", SUBJECTS, key="st_sub")
                category = st.selectbox("Category", CATEGORIES, key="st_cat")
                col_d, col_h, col_m = st.columns(3)
                study_date = col_d.date_input("Date", value=datetime.now().date(), key="st_date")
                hours = col_h.number_input("Hours", 0, 12, 1, key="st_hrs")
                mins  = col_m.number_input("Mins",  0, 59, 0, step=15, key="st_mins")
                duration = hours*60 + mins
                notes = st.text_input("Notes (optional)", placeholder="What did you study?", key="st_notes")
                if st.button("💾 Save Session", type="primary", use_container_width=True, key="save_session"):
                    if duration < 1:
                        st.error("Please enter a duration greater than 0.")
                    else:
                        db.execute_query(
                            "INSERT INTO study_sessions (date,subject,category,duration_minutes) VALUES (?,?,?,?)",
                            (str(study_date), subject, category, duration))
                        st.success(f"✅ Logged **{hours}h {mins}m** for **{subject}** ({category})")
                        st.balloons()

        with col_recent:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:15px;font-weight:700;color:{t['text']};margin-bottom:12px;'>Quick Stats — Today</div>", unsafe_allow_html=True)
                today = datetime.now().strftime("%Y-%m-%d")
                df_t = db.fetch_data(
                    "SELECT subject,category,duration_minutes FROM study_sessions WHERE date=? ORDER BY rowid DESC",
                    (today,))
                if df_t.empty:
                    st.info("Nothing logged today yet.")
                else:
                    total_m  = int(df_t["duration_minutes"].sum())
                    goal_m   = 360
                    pct_goal = min(100, int(total_m/goal_m*100))
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                      <div>
                        <div style="font-size:28px;font-weight:800;color:{accent};font-family:'JetBrains Mono',monospace;">{total_m//60}h {total_m%60}m</div>
                        <div style="font-size:11px;color:{t['text3']};text-transform:uppercase;letter-spacing:1px;">Today's total</div>
                      </div>
                      <div style="font-size:13px;color:{accent};font-weight:700;">{pct_goal}% of 6h goal</div>
                    </div>
                    <div style="height:6px;background:{t['border']};border-radius:999px;margin-bottom:14px;">
                      <div style="height:100%;width:{pct_goal}%;background:linear-gradient(90deg,{accent},{accent2});border-radius:999px;"></div>
                    </div>""", unsafe_allow_html=True)
                    for _, row in df_t.iterrows():
                        color = SUBJECT_COLORS.get(row["subject"],"#6366f1")
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid {t['border']};">
                          <div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;"></div>
                          <span style="color:{color};font-weight:700;font-size:13px;width:44px;">{row['subject']}</span>
                          <span style="color:{t['text2']};font-size:12px;flex:1;">{row['category']}</span>
                          <span style="color:{t['text']};font-weight:600;font-size:13px;font-family:'JetBrains Mono',monospace;">{int(row['duration_minutes'])}m</span>
                        </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # TAB 1 – POMODORO
    # ══════════════════════════════════════════════════════
    with tabs[1]:
        st.markdown(f"""
        <div style="text-align:center;padding:10px 0 24px;">
          <div style="font-size:20px;font-weight:800;color:{t['text']};margin-bottom:6px;">🍅 Pomodoro Technique</div>
          <div style="font-size:13px;color:{t['text2']};">Focus 50 min → Break 10 min → Repeat</div>
        </div>""", unsafe_allow_html=True)
        col_f, col_b = st.columns(2)
        with col_f:
            with st.container(border=True):
                st.markdown(f"""
                <div style="text-align:center;padding:16px 0;">
                  <div style="font-size:48px;">🎯</div>
                  <div style="font-size:20px;font-weight:800;color:{accent2};margin:8px 0;">50 Min Focus</div>
                  <div style="font-size:12px;color:{t['text2']};">Deep work, no distractions</div>
                </div>""", unsafe_allow_html=True)
                pomo_sub = st.selectbox("Subject to log", SUBJECTS, key="pomo_sub")
                if st.button("▶️ Start Focus Session", type="primary", use_container_width=True):
                    st.session_state["pomo_active"] = True
                    st.session_state["pomo_type"]   = "Focus"
                    st.session_state["pomo_sub"]    = pomo_sub
                    st.info("🎯 Focus session started! Study hard for 50 minutes.")
        with col_b:
            with st.container(border=True):
                st.markdown(f"""
                <div style="text-align:center;padding:16px 0;">
                  <div style="font-size:48px;">☕</div>
                  <div style="font-size:20px;font-weight:800;color:{accent};margin:8px 0;">10 Min Break</div>
                  <div style="font-size:12px;color:{t['text2']};">Rest, hydrate, stretch</div>
                </div>""", unsafe_allow_html=True)
                st.write("")
                if st.button("☕ Start Break", use_container_width=True):
                    st.session_state["pomo_active"] = True
                    st.session_state["pomo_type"]   = "Break"
                    st.info("☕ Break started! Relax for 10 minutes.")
        if st.session_state.get("pomo_active"):
            ptype = st.session_state.get("pomo_type","Focus")
            clr   = accent2 if ptype == "Focus" else accent
            st.markdown(f"""
            <div style="margin-top:16px;padding:18px 20px;background:{clr}10;
                 border:1px solid {clr}44;border-radius:14px;text-align:center;">
              <span style="color:{clr};font-weight:700;font-size:15px;">
                {'🎯 Focus' if ptype=='Focus' else '☕ Break'} session is ACTIVE</span>
            </div>""", unsafe_allow_html=True)
            if st.button("⏹️ End & Log Session", use_container_width=True):
                if ptype == "Focus":
                    sub = st.session_state.get("pomo_sub","FR")
                    db.execute_query(
                        "INSERT INTO study_sessions (date,subject,category,duration_minutes) VALUES (?,?,?,?)",
                        (datetime.now().strftime("%Y-%m-%d"), sub, "Self Study", 50))
                    st.success("✅ 50-min session auto-logged!")
                st.session_state["pomo_active"] = False
                st.rerun()

    # ══════════════════════════════════════════════════════
    # TAB 2 – HISTORY & STATS
    # ══════════════════════════════════════════════════════
    with tabs[2]:
        df = db.fetch_data("SELECT date,subject,category,duration_minutes FROM study_sessions ORDER BY date DESC,rowid DESC")
        if df.empty:
            st.info("No sessions logged yet. Start with the Log Session tab!")
        else:
            df["hours"] = (df["duration_minutes"]/60).round(2)
            total_h = df["hours"].sum()
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Total Sessions", len(df))
            c2.metric("Total Hours",    f"{total_h:.1f}h")
            c3.metric("Avg Session",    f"{df['duration_minutes'].mean():.0f} min")
            best_day = df.groupby("date")["duration_minutes"].sum().max()/60
            c4.metric("Best Day",       f"{best_day:.1f}h")

            col_chart, col_table = st.columns([1,2])
            with col_chart:
                with st.container(border=True):
                    cat_g = df.groupby("category")["hours"].sum().reset_index()
                    CAT_COLORS = {"Self Study":accent,"Lectures":accent2,"Revision":accent3,"Practice":accent4,"Mock Test":accent5}
                    fig = go.Figure(go.Pie(
                        labels=cat_g["category"], values=cat_g["hours"].round(1),
                        hole=0.58,
                        marker=dict(colors=[CAT_COLORS.get(c,"#6366f1") for c in cat_g["category"]],
                        line=dict(color="#080c14",width=3)),
                        textinfo="label+percent", textfont=dict(size=11,color=t["text"])
                    ))
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=t["text2"],size=11,family="DM Sans,sans-serif"),
                        margin=dict(l=0,r=0,t=0,b=0), height=210, showlegend=False,
                        title=dict(text="By Category",font=dict(color=t["text"],size=13),x=0.5)
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
                with st.container(border=True):
                    df2 = df.copy()
                    df2["date"] = pd.to_datetime(df2["date"])
                    weekly = df2.groupby(df2["date"].dt.isocalendar().week)["hours"].sum().tail(8).reset_index()
                    weekly.columns = ["week","hours"]
                    fig2 = go.Figure(go.Bar(
                        x=[f"Wk {w}" for w in weekly["week"]], y=weekly["hours"],
                        marker=dict(color=accent, opacity=0.8, line=dict(width=0)),
                    ))
                    fig2.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=t["text2"],size=11),
                        xaxis=dict(showgrid=False,linecolor=t["border"]),
                        yaxis=dict(showgrid=True,gridcolor=t["plot_grid"],zeroline=False),
                        margin=dict(l=0,r=0,t=0,b=0), height=160,
                        title=dict(text="Weekly Hours",font=dict(color=t["text"],size=13),x=0)
                    )
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
            with col_table:
                with st.container(border=True):
                    display = df[["date","subject","category","duration_minutes"]].copy()
                    display.columns = ["Date","Subject","Category","Minutes"]
                    st.dataframe(display.head(25), use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════════
    # TAB 3 – PROGRESS TRACKER
    # ══════════════════════════════════════════════════════
    with tabs[3]:
        _ensure_topic_table()

        st.markdown(f"""
        <div style="margin-bottom:20px;">
          <div style="font-size:22px;font-weight:800;color:{t['text']};letter-spacing:-0.04em;">
            📚 Topic Progress Tracker</div>
          <div style="font-size:13px;color:{t['text2']};margin-top:4px;">
            Track every topic, set confidence levels, and monitor completion</div>
        </div>""", unsafe_allow_html=True)

        # ── Subject readiness cards ─────────────────────────
        st.markdown(f"<div style='font-size:11px;font-weight:700;color:{t['text3']};text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>SUBJECT READINESS</div>", unsafe_allow_html=True)
        sub_cols = st.columns(6)
        for i, sub in enumerate(SUBJECTS):
            df_sub = db.fetch_data("SELECT status,confidence FROM topic_progress WHERE subject=?", (sub,))
            if df_sub.empty:
                _load_topics(sub)
                df_sub = db.fetch_data("SELECT status,confidence FROM topic_progress WHERE subject=?", (sub,))
            if "status" not in df_sub.columns:
                df_sub["status"] = "Not Started"
            if "confidence" not in df_sub.columns:
                df_sub["confidence"] = 0
            total  = len(df_sub)
            done   = len(df_sub[df_sub["status"]=="Completed"])
            pct    = round(done/total*100) if total else 0
            non_zero = df_sub[df_sub["confidence"]>0]
            conf   = round(non_zero["confidence"].mean()) if not non_zero.empty else 0
            clr    = SUBJECT_COLORS[sub]
            with sub_cols[i]:
                st.markdown(f"""
                <div style="background:{clr}0a;border:1px solid {clr}22;border-radius:14px;
                     padding:14px 10px;text-align:center;">
                  <div style="font-size:22px;margin-bottom:4px;">{SUBJECT_ICONS[sub]}</div>
                  <div style="font-size:11px;font-weight:700;color:{clr};margin-bottom:8px;">{sub}</div>
                  <div style="font-size:22px;font-weight:800;color:{t['text']};
                       font-family:'JetBrains Mono',monospace;line-height:1;">{pct}%</div>
                  <div style="font-size:10px;color:{t['text3']};margin-bottom:8px;">{done}/{total} done</div>
                  <div style="height:4px;background:{t['border']};border-radius:999px;">
                    <div style="height:100%;width:{pct}%;background:{clr};border-radius:999px;"></div>
                  </div>
                  <div style="font-size:10px;color:{t['text3']};margin-top:6px;">conf {conf}%</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        # ── Subject tabs (like React app) ───────────────────
        sub_tab_labels = [f"{SUBJECT_ICONS[s]} {s}" for s in SUBJECTS]
        sub_tabs = st.tabs(sub_tab_labels)

        for tab_idx, active_sub in enumerate(SUBJECTS):
            with sub_tabs[tab_idx]:
                clr = SUBJECT_COLORS[active_sub]

                # Add topic button row
                col_hdr, col_add_btn = st.columns([5,1])
                with col_hdr:
                    st.markdown(f"<div style='font-size:14px;font-weight:700;color:{t['text']};padding:6px 0;'>{SUBJECT_ICONS[active_sub]} {SUBJECT_FULL[active_sub]}</div>", unsafe_allow_html=True)
                with col_add_btn:
                    if st.button("＋ Add", key=f"add_btn_{active_sub}", type="primary", use_container_width=True):
                        st.session_state[f"pt_show_add_{active_sub}"] = not st.session_state.get(f"pt_show_add_{active_sub}", False)

                # Add topic form
                if st.session_state.get(f"pt_show_add_{active_sub}", False):
                    with st.container(border=True):
                        st.markdown(f"<div style='font-size:13px;font-weight:700;color:{clr};margin-bottom:10px;'>Add New Topic to {active_sub}</div>", unsafe_allow_html=True)
                        a1, a2 = st.columns([4,1])
                        new_name = a1.text_input("Topic Name", placeholder="e.g. Ind AS 109 – Financial Instruments", key=f"pt_new_name_{active_sub}")
                        new_hrs  = a2.number_input("Hours", 1, 40, 8, key=f"pt_new_hrs_{active_sub}")
                        if st.button("✅ Add Topic", type="primary", key=f"pt_submit_{active_sub}"):
                            if new_name.strip():
                                db.execute_query(
                                    "INSERT INTO topic_progress (subject,topic_name,estimated_hours,status,confidence,added_date) VALUES (?,?,?,?,?,?)",
                                    (active_sub, new_name.strip(), new_hrs, "Not Started", 0, str(date.today())))
                                st.session_state[f"pt_show_add_{active_sub}"] = False
                                st.success("✅ Topic added!")
                                st.rerun()

                # Load topics
                df_topics = _load_topics(active_sub)

                # Summary bar
                total   = len(df_topics)
                done    = len(df_topics[df_topics["status"]=="Completed"])
                in_prog = len(df_topics[df_topics["status"]=="In Progress"])
                not_st  = total - done - in_prog
                pct_done = round(done/total*100) if total else 0
                est_hrs  = df_topics["estimated_hours"].sum()
                done_hrs = df_topics[df_topics["status"]=="Completed"]["estimated_hours"].sum()

                st.markdown(f"""
                <div style="background:{clr}08;border:1px solid {clr}22;border-radius:14px;
                     padding:14px 18px;margin:10px 0 14px;display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
                  <div>
                    <div style="font-size:26px;font-weight:800;color:{clr};
                         font-family:'JetBrains Mono',monospace;">{pct_done}%</div>
                    <div style="font-size:10px;color:{t['text3']};text-transform:uppercase;letter-spacing:1px;">Complete</div>
                  </div>
                  <div style="flex:1;min-width:160px;">
                    <div style="height:7px;background:{t['border']};border-radius:999px;margin-bottom:8px;">
                      <div style="height:100%;width:{pct_done}%;background:{clr};border-radius:999px;"></div>
                    </div>
                    <div style="display:flex;gap:14px;font-size:11px;">
                      <span style="color:#00f5c4;">✅ {done} done</span>
                      <span style="color:#f5a623;">🔄 {in_prog} in progress</span>
                      <span style="color:{t['text3']};">⭕ {not_st} not started</span>
                    </div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:14px;font-weight:700;color:{t['text']};
                         font-family:'JetBrains Mono',monospace;">{done_hrs:.0f}/{est_hrs:.0f}h</div>
                    <div style="font-size:10px;color:{t['text3']};">Hours covered</div>
                  </div>
                </div>""", unsafe_allow_html=True)

                # Topic rows
                for _, row in df_topics.iterrows():
                    tid    = int(row["id"])
                    status = row["status"]
                    conf   = int(row["confidence"])
                    sc     = STATUS_COLORS[status]
                    si     = STATUS_ICONS[status]
                    conf_clr = "#00f5c4" if conf>=75 else "#f5a623" if conf>=40 else ("#ff6b9d" if conf>0 else t["text3"])

                    with st.container(border=True):
                        r1, r2, r3, r4 = st.columns([4, 2, 2, 1])

                        with r1:
                            st.markdown(f"""
                            <div style="padding:4px 0;">
                              <div style="font-size:14px;font-weight:600;color:{t['text']};margin-bottom:3px;">
                                {si} {row['topic_name']}</div>
                              <div style="font-size:11px;color:{t['text3']};">{row['estimated_hours']}h estimated</div>
                              <div style="margin-top:7px;height:4px;background:{t['border']};border-radius:999px;max-width:280px;">
                                <div style="height:100%;width:{conf}%;background:{conf_clr};border-radius:999px;"></div>
                              </div>
                            </div>""", unsafe_allow_html=True)

                        with r2:
                            new_status = st.selectbox(
                                "Status",
                                ["Not Started","In Progress","Completed"],
                                index=["Not Started","In Progress","Completed"].index(status),
                                key=f"pt_status_{tid}",
                                )
                            if new_status != status:
                                auto_conf = max(conf, 70) if new_status=="Completed" else conf
                                db.execute_query(
                                    "UPDATE topic_progress SET status=?,confidence=? WHERE id=?",
                                    (new_status, auto_conf, tid))
                                st.rerun()

                        with r3:
                            st.markdown(f"<div style='font-size:11px;color:{t['text3']};padding-top:6px;'>Confidence: <b style='color:{conf_clr};'>{conf}%</b></div>", unsafe_allow_html=True)
                            new_conf = st.slider("conf", 0, 100, conf,
                                key=f"pt_conf_{tid}")
                            if new_conf != conf:
                                db.execute_query("UPDATE topic_progress SET confidence=? WHERE id=?", (new_conf, tid))

                        with r4:
                            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                            if st.button("🗑️", key=f"pt_del_{tid}", help="Delete topic"):
                                db.execute_query("DELETE FROM topic_progress WHERE id=?", (tid,))
                                st.rerun()

        # ── Radar chart overview ────────────────────────────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:11px;font-weight:700;color:{t['text3']};text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;'>CONFIDENCE VS COMPLETION — ALL SUBJECTS</div>", unsafe_allow_html=True)

        radar_c1, radar_c2 = st.columns(2)
        with radar_c1:
            with st.container(border=True):
                conf_vals, comp_vals = [], []
                for sub in SUBJECTS:
                    dfx = db.fetch_data("SELECT status,confidence FROM topic_progress WHERE subject=?", (sub,))
                    if dfx.empty:
                        dfx = pd.DataFrame({"status":[],"confidence":[]})
                    nz = dfx[dfx["confidence"]>0]
                    conf_vals.append(round(nz["confidence"].mean()) if not nz.empty else 0)
                    comp_vals.append(round(len(dfx[dfx["status"]=="Completed"])/len(dfx)*100) if len(dfx) else 0)

                fig_r = go.Figure()
                fig_r.add_trace(go.Scatterpolar(
                    r=conf_vals+[conf_vals[0]], theta=SUBJECTS+[SUBJECTS[0]],
                    fill="toself", name="Confidence",
                    line=dict(color=accent,width=2), fillcolor="rgba(0,245,196,0.10)"))
                fig_r.add_trace(go.Scatterpolar(
                    r=comp_vals+[comp_vals[0]], theta=SUBJECTS+[SUBJECTS[0]],
                    fill="toself", name="Completion",
                    line=dict(color=accent2,width=2), fillcolor="rgba(123,104,238,0.10)"))
                fig_r.update_layout(
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True,range=[0,100],
                            gridcolor=t["plot_grid"],tickfont=dict(color=t["text2"],size=9)),
                        angularaxis=dict(gridcolor=t["plot_grid"],
                            tickfont=dict(color=t["text"],size=11,family="DM Sans"))),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=t["text2"],size=11),
                    legend=dict(bgcolor="rgba(0,0,0,0)",bordercolor="rgba(0,0,0,0)",
                        font=dict(color=t["text"],size=11)),
                    margin=dict(l=30,r=30,t=10,b=10), height=280)
                st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar":False})

        with radar_c2:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:13px;font-weight:700;color:{t['text']};margin-bottom:14px;'>All Subjects at a Glance</div>", unsafe_allow_html=True)
                for sub in SUBJECTS:
                    dfx = db.fetch_data("SELECT status,confidence FROM topic_progress WHERE subject=?", (sub,))
                    if dfx.empty:
                        continue
                    total_s = len(dfx)
                    done_s  = len(dfx[dfx["status"]=="Completed"])
                    pct_s   = round(done_s/total_s*100) if total_s else 0
                    nz      = dfx[dfx["confidence"]>0]
                    conf_s  = round(nz["confidence"].mean()) if not nz.empty else 0
                    clr_s   = SUBJECT_COLORS[sub]
                    st.markdown(f"""
                    <div style="margin-bottom:12px;">
                      <div style="display:flex;justify-content:space-between;margin-bottom:5px;align-items:center;">
                        <span style="font-size:13px;font-weight:600;color:{t['text']};">{SUBJECT_ICONS[sub]} {sub}</span>
                        <div style="display:flex;gap:8px;align-items:center;">
                          <span style="font-size:11px;background:{clr_s}15;color:{clr_s};padding:2px 8px;
                               border-radius:99px;border:1px solid {clr_s}30;font-weight:600;">conf {conf_s}%</span>
                          <span style="font-size:13px;color:{clr_s};font-weight:700;
                               font-family:'JetBrains Mono',monospace;">{pct_s}%</span>
                        </div>
                      </div>
                      <div style="height:6px;background:{t['border']};border-radius:999px;">
                        <div style="height:100%;width:{pct_s}%;background:linear-gradient(90deg,{clr_s},{clr_s}88);border-radius:999px;"></div>
                      </div>
                    </div>""", unsafe_allow_html=True)
