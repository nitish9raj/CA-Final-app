import streamlit as st
import database as db
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from theme import get_theme

SUBJECTS = ["FR","AFM","Audit","DT","IDT","IBS"]
SUBJECT_FULL = {
    "FR":"Financial Reporting","AFM":"Advanced Financial Mgmt",
    "Audit":"Advanced Auditing","DT":"Direct Tax Laws",
    "IDT":"Indirect Tax Laws","IBS":"Integrated Business Solutions",
}
SC = {"FR":"#00f5c4","AFM":"#7b68ee","Audit":"#f5a623","DT":"#ff6b9d","IDT":"#56ccf2","IBS":"#a78bfa"}


def _circ(value, color, size=90):
    r = (size-10)//2
    c = 2*3.14159*r
    off = c - (value/100)*c
    cx = size//2
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="6"/>'
            f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="{color}" stroke-width="6"'
            f' stroke-dasharray="{c:.1f}" stroke-dashoffset="{off:.1f}"'
            f' stroke-linecap="round" transform="rotate(-90 {cx} {cx})"/>'
            f'<text x="{cx}" y="{cx+5}" text-anchor="middle" fill="white"'
            f' font-size="14" font-weight="700" font-family="JetBrains Mono,monospace">{value}%</text>'
            f'</svg>')


def render_tests_analytics():
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
        📉 Tests & Analytics</div>
      <div style="font-size:13px;color:{t['text2']};margin-top:4px;">
        Track mock tests · Identify weak areas · ML-powered readiness insights</div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📝  Log Test", "📊  Score Analytics", "⚠️  Weak Areas", "🤖  AI Readiness"])

    # ══════════════════════════════════════════════════════
    # TAB 0 – LOG TEST
    # ══════════════════════════════════════════════════════
    with tabs[0]:
        col_f, col_h = st.columns([1,1])
        with col_f:
            with st.container(border=True):
                __text = t["text"]
                st.markdown(f"<div style='font-size:15px;font-weight:700;color:{__text};margin-bottom:14px;'>Log a Mock Test</div>", unsafe_allow_html=True)
                c1,c2 = st.columns(2)
                subject   = c1.selectbox("Subject", SUBJECTS, key="ts_sub",
                    format_func=lambda s: f"{s} – {SUBJECT_FULL[s]}")
                test_date = c2.date_input("Date", value=datetime.now().date(), key="ts_date")
                c3,c4 = st.columns(2)
                marks = c3.number_input("Marks Obtained", 0, 150, 70, key="ts_marks")
                total = c4.number_input("Total Marks",    1, 150, 100, key="ts_total")
                pct   = round(marks/total*100,1) if total>0 else 0
                g_clr = "#00f5c4" if pct>=75 else "#f5a623" if pct>=50 else "#ff6b9d"
                grade = "Excellent 🏆" if pct>=75 else "Good 👍" if pct>=50 else "Needs Work ⚠️"
                st.markdown(f"""
                <div style="background:{g_clr}08;border:1px solid {g_clr}33;
                     border-radius:14px;padding:16px;text-align:center;margin:12px 0;">
                  <div style="font-size:36px;font-weight:800;color:{g_clr};
                       font-family:'JetBrains Mono',monospace;line-height:1;">{pct}%</div>
                  <div style="font-size:13px;color:{g_clr};margin-top:4px;font-weight:600;">{grade}</div>
                  <div style="height:6px;background:rgba(255,255,255,0.06);border-radius:999px;margin-top:10px;">
                    <div style="height:100%;width:{pct}%;background:{g_clr};border-radius:999px;"></div>
                  </div>
                </div>""", unsafe_allow_html=True)
                weak = st.text_area("Weak Areas / Topics",
                    placeholder="e.g. Consolidation, Derivative Accounting",
                    key="ts_weak", height=80)
                if st.button("💾 Save Test Result", type="primary", use_container_width=True):
                    db.execute_query(
                        "INSERT INTO mock_tests (date,subject,marks_obtained,total_marks,weak_areas) VALUES (?,?,?,?,?)",
                        (str(test_date), subject, int(marks), int(total), weak))
                    st.success(f"✅ Saved! {marks}/{total} ({pct}%)")
                    st.balloons()

        with col_h:
            with st.container(border=True):
                __text = t["text"]
                st.markdown(f"<div style='font-size:15px;font-weight:700;color:{__text};margin-bottom:14px;'>Recent Test Results</div>", unsafe_allow_html=True)
                df_r = db.fetch_data("SELECT date,subject,marks_obtained,total_marks FROM mock_tests ORDER BY date DESC LIMIT 10")
                if df_r.empty:
                    st.markdown(f"""
                    <div style="padding:40px;text-align:center;">
                      <div style="font-size:40px;margin-bottom:8px;">📊</div>
                      <div style="font-size:13px;color:{t['text2']};">No tests logged yet.<br>Log your first mock test!</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    for _, row in df_r.iterrows():
                        p    = round(row["marks_obtained"]/row["total_marks"]*100,1)
                        sc   = SC.get(str(row["subject"]), accent)
                        bclr = "#00f5c4" if p>=75 else "#f5a623" if p>=50 else "#ff6b9d"
                        gi   = "🏆" if p>=75 else "✅" if p>=50 else "⚠️"
                        st.markdown(f"""
                        <div style="margin-bottom:10px;padding:12px 16px;
                             background:{sc}06;border:1px solid {sc}22;
                             border-left:3px solid {sc};border-radius:12px;">
                          <div style="display:flex;justify-content:space-between;margin-bottom:7px;align-items:center;">
                            <span style="color:{sc};font-weight:700;font-size:13px;">{row['subject']}</span>
                            <div style="display:flex;align-items:center;gap:8px;">
                              <span style="font-size:11px;color:{t['text3']};">{row['date']}</span>
                              <span style="font-size:15px;font-weight:800;color:{bclr};
                                   font-family:'JetBrains Mono',monospace;">{gi} {p}%</span>
                            </div>
                          </div>
                          <div style="height:5px;background:{t['border']};border-radius:999px;">
                            <div style="height:100%;width:{p}%;background:{bclr};border-radius:999px;"></div>
                          </div>
                          <div style="font-size:11px;color:{t['text3']};margin-top:5px;">
                            {row['marks_obtained']}/{row['total_marks']} marks</div>
                        </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # TAB 1 – SCORE ANALYTICS
    # ══════════════════════════════════════════════════════
    with tabs[1]:
        df = db.fetch_data("SELECT date,subject,marks_obtained,total_marks FROM mock_tests ORDER BY date")
        if df.empty:
            st.info("Log mock tests to see score analytics.")
        else:
            df["pct"]  = (df["marks_obtained"]/df["total_marks"]*100).round(1)
            df["date"] = pd.to_datetime(df["date"])

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Tests Taken", len(df))
            c2.metric("Avg Score",   f"{df['pct'].mean():.1f}%")
            c3.metric("Best Score",  f"{df['pct'].max():.1f}%")
            c4.metric("Last Score",  f"{df['pct'].iloc[-1]:.1f}%")

            with st.container(border=True):
                __text = t["text"]
                st.markdown(f"<div style='font-size:14px;font-weight:700;color:{__text};margin-bottom:12px;'>Score Trend by Subject</div>", unsafe_allow_html=True)
                fig = go.Figure()
                for subj in df["subject"].unique():
                    ds = df[df["subject"]==subj].sort_values("date")
                    fig.add_trace(go.Scatter(
                        x=ds["date"], y=ds["pct"], mode="lines+markers", name=subj,
                        line=dict(color=SC.get(subj,accent),width=2.5),
                        marker=dict(size=7,line=dict(width=2,color=SC.get(subj,accent))),
                        hovertemplate=f"<b>{subj}</b><br>%{{y:.1f}}%<extra></extra>"))
                fig.add_hline(y=60, line_dash="dash", line_color=t["border2"],
                    annotation_text="Pass 60%", annotation_font_color=t["text2"])
                fig.add_hline(y=75, line_dash="dot", line_color="rgba(0,245,196,0.25)",
                    annotation_text="Excellent 75%", annotation_font_color=accent)
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=t["text2"],size=11,family="DM Sans,sans-serif"),
                    xaxis=dict(showgrid=False,linecolor=t["border"]),
                    yaxis=dict(showgrid=True,gridcolor=t["plot_grid"],range=[0,105],zeroline=False),
                    legend=dict(bgcolor="rgba(0,0,0,0)",bordercolor=t["border"],font=dict(color=t["text"],size=11)),
                    margin=dict(l=0,r=0,t=8,b=0), height=260)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            col_bar, col_dist = st.columns(2)
            with col_bar:
                with st.container(border=True):
                    __text = t["text"]
                    st.markdown(f"<div style='font-size:14px;font-weight:700;color:{__text};margin-bottom:12px;'>Average Score by Subject</div>", unsafe_allow_html=True)
                    sub_avg = df.groupby("subject")["pct"].mean().round(1)
                    fig2 = go.Figure(go.Bar(
                        x=sub_avg.index.tolist(), y=sub_avg.values.tolist(),
                        marker=dict(color=[SC.get(s,accent) for s in sub_avg.index],
                            opacity=0.85, line=dict(width=0)),
                        text=[f"{v}%" for v in sub_avg.values],
                        textposition="outside", textfont=dict(color=t["text"],size=11)
                    ))
                    fig2.add_hline(y=60, line_dash="dash", line_color=t["border2"])
                    fig2.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=t["text2"],size=11),
                        xaxis=dict(showgrid=False,linecolor=t["border"]),
                        yaxis=dict(showgrid=True,gridcolor=t["plot_grid"],range=[0,115],zeroline=False),
                        margin=dict(l=0,r=0,t=8,b=0), height=220)
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

            with col_dist:
                with st.container(border=True):
                    __text = t["text"]
                    st.markdown(f"<div style='font-size:14px;font-weight:700;color:{__text};margin-bottom:12px;'>Score Distribution</div>", unsafe_allow_html=True)
                    bins_lbl = ["<40%","40-50%","50-60%","60-75%","75%+"]
                    bins_val = [
                        len(df[df["pct"]<40]),
                        len(df[(df["pct"]>=40)&(df["pct"]<50)]),
                        len(df[(df["pct"]>=50)&(df["pct"]<60)]),
                        len(df[(df["pct"]>=60)&(df["pct"]<75)]),
                        len(df[df["pct"]>=75]),
                    ]
                    bins_clr = ["#ff6b9d","#f87171","#f5a623","#56ccf2","#00f5c4"]
                    fig3 = go.Figure(go.Bar(
                        x=bins_lbl, y=bins_val,
                        marker=dict(color=bins_clr, opacity=0.85, line=dict(width=0)),
                        text=bins_val, textposition="outside",
                        textfont=dict(color=t["text"],size=11)
                    ))
                    fig3.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=t["text2"],size=11),
                        xaxis=dict(showgrid=False,linecolor=t["border"]),
                        yaxis=dict(showgrid=True,gridcolor=t["plot_grid"],zeroline=False),
                        margin=dict(l=0,r=0,t=8,b=0), height=220)
                    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    # ══════════════════════════════════════════════════════
    # TAB 2 – WEAK AREAS
    # ══════════════════════════════════════════════════════
    with tabs[2]:
        df_w = db.fetch_data("SELECT subject,weak_areas FROM mock_tests WHERE weak_areas IS NOT NULL AND weak_areas != ''")
        if df_w.empty:
            st.info("Add weak areas when logging tests to see analysis here.")
        else:
            __text = t["text"]
            st.markdown(f"<div style='font-size:15px;font-weight:700;color:{__text};margin-bottom:16px;'>Weak Area Analysis</div>", unsafe_allow_html=True)
            for subj in SUBJECTS:
                rows = df_w[df_w["subject"]==subj]
                if rows.empty:
                    continue
                areas = [a.strip() for r in rows["weak_areas"] for a in str(r).split(",") if a.strip()]
                clr   = SC.get(subj, accent)
                freq  = {}
                for a in areas:
                    freq[a] = freq.get(a,0)+1
                freq_sorted = sorted(freq.items(), key=lambda x: -x[1])
                chips = "".join(
                    f'<span style="display:inline-block;background:{clr}10;border:1px solid {clr}30;'
                    f'color:{clr};padding:4px 12px;border-radius:20px;font-size:11px;'
                    f'font-weight:600;margin:3px;">{a}{"&nbsp;×"+str(c) if c>1 else ""}</span>'
                    for a,c in freq_sorted)
                with st.container(border=True):
                    st.markdown(f"""
                    <div>
                      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                        <div style="width:10px;height:10px;border-radius:50%;background:{clr};"></div>
                        <span style="font-size:14px;font-weight:700;color:{clr};">{subj}</span>
                        <span style="font-size:11px;color:{t['text3']};">— {SUBJECT_FULL[subj]}</span>
                        <span style="margin-left:auto;font-size:11px;color:{t['text3']};
                             background:{t['border']};padding:2px 8px;border-radius:99px;">{len(areas)} mentions</span>
                      </div>
                      <div style="display:flex;flex-wrap:wrap;gap:2px;">{chips}</div>
                    </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # TAB 3 – AI READINESS DASHBOARD
    # ══════════════════════════════════════════════════════
    with tabs[3]:
        st.markdown(f"""
        <div style="margin-bottom:20px;">
          <div style="font-size:22px;font-weight:800;color:{t['text']};letter-spacing:-0.04em;">
            🤖 AI Readiness Dashboard</div>
          <div style="font-size:13px;color:{t['text2']};margin-top:4px;">
            Composite score based on your actual mock test results, study hours &amp; topic completion</div>
        </div>""", unsafe_allow_html=True)

        # ── Pull ALL data from DB ──────────────────────────
        df_tests      = db.fetch_data("SELECT date,subject,marks_obtained,total_marks FROM mock_tests ORDER BY date")
        df_sess_all   = db.fetch_data("SELECT date,subject,duration_minutes FROM study_sessions")
        try:
            df_topics_all = db.fetch_data("SELECT subject,status,confidence FROM topic_progress")
        except Exception:
            df_topics_all = pd.DataFrame({"subject":[],"status":[],"confidence":[]})

        # ── Compute aggregate metrics ──────────────────────
        avg_mock = round(df_tests["marks_obtained"].sum()/df_tests["total_marks"].sum()*100,1) if not df_tests.empty else 0
        total_hrs = round(df_sess_all["duration_minutes"].sum()/60,1) if not df_sess_all.empty else 0

        week_hrs = 0.0
        if not df_sess_all.empty:
            df_w7 = df_sess_all.copy()
            df_w7["date"] = pd.to_datetime(df_w7["date"])
            last7 = df_w7[df_w7["date"] >= (pd.Timestamp.now()-pd.Timedelta(days=7))]
            week_hrs = round(last7["duration_minutes"].sum()/60,1)

        topics_done  = len(df_topics_all[df_topics_all["status"]=="Completed"]) if not df_topics_all.empty else 0
        topics_total = max(len(df_topics_all), 1) if not df_topics_all.empty else 1
        completion   = round(topics_done/topics_total*100)
        nz_conf      = df_topics_all[df_topics_all["confidence"]>0] if not df_topics_all.empty else pd.DataFrame()
        avg_conf     = round(nz_conf["confidence"].mean()) if not nz_conf.empty else 0

        readiness    = min(100, round(
            (completion*0.35) + (avg_conf*0.30) + (min(avg_mock,100)*0.25) + min(week_hrs/6*10,10)))
        burnout_risk = week_hrs > 50

        # ── Per-subject score from actual test log ─────────
        sub_scores = {}
        sub_tests_count = {}
        for subj in SUBJECTS:
            if not df_tests.empty:
                ds = df_tests[df_tests["subject"]==subj]
                if not ds.empty:
                    sub_scores[subj]      = round(ds["marks_obtained"].sum()/ds["total_marks"].sum()*100,1)
                    sub_tests_count[subj] = len(ds)
                else:
                    sub_scores[subj]      = 0
                    sub_tests_count[subj] = 0
            else:
                sub_scores[subj]      = 0
                sub_tests_count[subj] = 0

        # ── Hero readiness card ────────────────────────────
        status_text = "🏆 Exam-Ready!" if readiness>=80 else "💪 Good Progress" if readiness>=60 else "📖 Needs Work"
        r_clr = "#00f5c4" if readiness>=80 else "#f5a623" if readiness>=60 else "#ff6b9d"
        desc = {
            "🏆 Exam-Ready!":   "Outstanding! Focus on mock tests and refining weak areas.",
            "💪 Good Progress": "You're on track. Increase revision frequency for weaker subjects.",
            "📖 Needs Work":    "Prioritize incomplete topics. Aim for 70%+ completion before mock tests.",
        }
        mock_clr  = "#00f5c4" if avg_mock>=75 else "#f5a623" if avg_mock>=50 else ("#ff6b9d" if avg_mock>0 else "#374151")
        conf_clr2 = "#00f5c4" if avg_conf>=70 else "#f5a623" if avg_conf>=40 else "#ff6b9d"
        comp_clr  = "#00f5c4" if completion>=70 else "#f5a623" if completion>=40 else "#ff6b9d"

        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.08);border-left:3px solid {r_clr};
             border-radius:20px;padding:24px 28px;margin-bottom:24px;
             display:flex;align-items:center;gap:32px;flex-wrap:wrap;">
          <div style="text-align:center;flex-shrink:0;">
            {_circ(readiness, r_clr, 110)}
            <div style="font-size:11px;color:{t['text3']};margin-top:6px;text-transform:uppercase;letter-spacing:1px;">Readiness Score</div>
          </div>
          <div style="flex:1;min-width:200px;">
            <div style="font-size:22px;font-weight:800;color:{t['text']};margin-bottom:8px;">{status_text}</div>
            <div style="font-size:13px;color:{t['text2']};line-height:1.6;margin-bottom:16px;">{desc[status_text]}</div>
            <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:flex-end;">
              <div style="text-align:center;">
                {_circ(completion, comp_clr, 78)}
                <div style="font-size:10px;color:{t['text3']};margin-top:4px;">Topic Completion</div>
                <div style="font-size:10px;color:{comp_clr};font-weight:600;">{topics_done}/{topics_total} topics</div>
              </div>
              <div style="text-align:center;">
                {_circ(avg_conf, conf_clr2, 78)}
                <div style="font-size:10px;color:{t['text3']};margin-top:4px;">Avg Confidence</div>
                <div style="font-size:10px;color:{conf_clr2};font-weight:600;">self-assessed</div>
              </div>
              <div style="text-align:center;">
                {_circ(int(avg_mock), mock_clr, 78)}
                <div style="font-size:10px;color:{t['text3']};margin-top:4px;">Mock Score Avg</div>
                <div style="font-size:10px;color:{mock_clr};font-weight:600;">{len(df_tests)} tests logged</div>
              </div>
            </div>
          </div>
          <div style="display:flex;flex-direction:column;gap:10px;flex-shrink:0;">
            <div style="background:{t['bg2']};border:1px solid {t['border']};border-radius:12px;padding:12px 18px;text-align:center;">
              <div style="font-size:22px;font-weight:800;color:{accent};font-family:'JetBrains Mono',monospace;">{total_hrs}h</div>
              <div style="font-size:10px;color:{t['text3']};text-transform:uppercase;letter-spacing:1px;">Total Studied</div>
            </div>
            <div style="background:{t['bg2']};border:1px solid {'rgba(255,107,157,0.3)' if burnout_risk else t['border']};border-radius:12px;padding:12px 18px;text-align:center;">
              <div style="font-size:22px;font-weight:800;color:{'#ff6b9d' if burnout_risk else accent3};font-family:'JetBrains Mono',monospace;">{week_hrs}h</div>
              <div style="font-size:10px;color:{t['text3']};text-transform:uppercase;letter-spacing:1px;">This Week</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Burnout warning ────────────────────────────────
        if burnout_risk:
            st.markdown(f"""
            <div style="background:rgba(255,107,157,0.04);border:1px solid rgba(255,107,157,0.27);
                 border-radius:14px;padding:18px 22px;margin-bottom:20px;
                 display:flex;align-items:center;gap:16px;">
              <div style="font-size:36px;">⚠️</div>
              <div>
                <div style="font-weight:800;color:#ff6b9d;font-size:16px;">Burnout Risk Detected</div>
                <div style="font-size:13px;color:{t['text2']};margin-top:4px;line-height:1.6;">
                  You've studied {week_hrs}h this week — above the healthy 50h threshold.
                  Take a mandatory half-day rest. Retention drops sharply after 6+ hours/day.</div>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Per-subject circular rings from test log ───────
        __text3 = t["text3"]
        st.markdown(f"<div style='font-size:11px;font-weight:700;color:{__text3};text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;'>MOCK TEST SCORE PER SUBJECT (from your logged tests)</div>", unsafe_allow_html=True)

        sub_ring_cols = st.columns(6)
        for i, subj in enumerate(SUBJECTS):
            score      = sub_scores[subj]
            n_tests    = sub_tests_count[subj]
            clr_subj   = SC[subj]
            ring_clr   = "#00f5c4" if score>=75 else "#f5a623" if score>=50 else ("#ff6b9d" if score>0 else "#374151")
            label_line = f"{n_tests} test{'s' if n_tests!=1 else ''} logged" if n_tests else "No tests yet"
            with sub_ring_cols[i]:
                st.markdown(f"""
                <div style="background:{clr_subj}08;border:1px solid {clr_subj}20;border-radius:14px;
                     padding:14px 10px;text-align:center;">
                  {_circ(int(score), ring_clr, 72)}
                  <div style="font-size:12px;font-weight:700;color:{clr_subj};margin-top:6px;">{subj}</div>
                  <div style="font-size:10px;color:{t['text3']};margin-top:2px;">{label_line}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # ── Bottom two columns ─────────────────────────────
        col_left, col_right = st.columns(2)

        with col_left:
            with st.container(border=True):
                __text = t["text"]
                st.markdown(f"<div style='font-size:14px;font-weight:700;color:{__text};margin-bottom:14px;'>Score by Subject — Bar View</div>", unsafe_allow_html=True)
                for subj in SUBJECTS:
                    avg_s  = sub_scores[subj]
                    n_t    = sub_tests_count[subj]
                    clr    = SC[subj]
                    bar_c  = "#00f5c4" if avg_s>=75 else "#f5a623" if avg_s>=50 else ("#ff6b9d" if avg_s>0 else t["border"])
                    label  = f"{avg_s}% avg · {n_t} test{'s' if n_t!=1 else ''}" if n_t else "No tests logged"
                    st.markdown(f"""
                    <div style="margin-bottom:12px;">
                      <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                        <span style="font-size:13px;font-weight:600;color:{t['text']};">{subj}</span>
                        <span style="font-size:12px;color:{bar_c};font-weight:600;
                             font-family:'JetBrains Mono',monospace;">{label}</span>
                      </div>
                      <div style="height:7px;background:{t['border']};border-radius:999px;">
                        <div style="height:100%;width:{avg_s}%;background:linear-gradient(90deg,{bar_c},{bar_c}88);border-radius:999px;transition:width 0.6s;"></div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                if df_tests.empty:
                    st.info("Log mock tests in the Log Test tab to populate this chart.")

        with col_right:
            with st.container(border=True):
                __text = t["text"]
                st.markdown(f"<div style='font-size:14px;font-weight:700;color:{__text};margin-bottom:14px;'>📌 AI Recommendations</div>", unsafe_allow_html=True)
                recs = []
                for subj in SUBJECTS:
                    avg_s = sub_scores[subj]
                    n_t   = sub_tests_count[subj]
                    if n_t > 0:
                        if avg_s < 50:
                            recs.append(("🔴","#ff6b9d",f"Critical: {subj} — {avg_s}%",
                                f"Below pass mark. Schedule 2h daily deep study for {subj}."))
                        elif avg_s < 65:
                            recs.append(("🟡","#f5a623",f"Improve: {subj} — {avg_s}%",
                                f"Below 65%. Increase practice questions and revisions."))
                if not df_topics_all.empty:
                    not_started = len(df_topics_all[df_topics_all["status"]=="Not Started"])
                    if not_started > 0:
                        recs.append(("📖",accent2,f"{not_started} topics not started",
                            "Start with high-weightage topics first."))
                if week_hrs < 20:
                    recs.append(("⏰",accent5,"Low study hours this week",
                        f"Only {week_hrs}h logged. Aim for 30-40h/week."))
                if readiness >= 70:
                    recs.append(("✅",accent,"Strong preparation momentum",
                        "Readiness is solid. Keep up revision and mock test frequency."))
                if df_tests.empty:
                    recs.append(("📝",accent,"Log your first mock test",
                        "Go to the Log Test tab to record your mock test results and unlock AI insights."))
                if not recs:
                    recs.append(("📊",accent,"All subjects on track!",
                        "Great work. Stay consistent with revisions and mock tests."))
                for icon, clr, title, body in recs[:5]:
                    st.markdown(f"""
                    <div style="background:{clr}08;border:1px solid {clr}20;border-radius:12px;
                         padding:12px 14px;margin-bottom:10px;">
                      <div style="font-size:13px;font-weight:700;color:{clr};margin-bottom:4px;">{icon} {title}</div>
                      <div style="font-size:12px;color:{t['text2']};line-height:1.6;">{body}</div>
                    </div>""", unsafe_allow_html=True)

        # ── Weekly study heatmap ───────────────────────────
        if not df_sess_all.empty:
            with st.container(border=True):
                __text = t["text"]
                st.markdown(f"<div style='font-size:14px;font-weight:700;color:{__text};margin-bottom:14px;'>Weekly Study Hours — Last 8 Weeks</div>", unsafe_allow_html=True)
                df_s3 = df_sess_all.copy()
                df_s3["date"] = pd.to_datetime(df_s3["date"])
                df_s3["week"] = df_s3["date"].dt.isocalendar().week.astype(str)
                week_sub = df_s3.groupby(["week","subject"])["duration_minutes"].sum().reset_index()
                week_sub["hours"] = week_sub["duration_minutes"]/60
                if not week_sub.empty:
                    pivot = week_sub.pivot(index="subject",columns="week",values="hours").fillna(0)
                    pivot = pivot[sorted(pivot.columns)[-8:]]
                    fig_h = go.Figure(go.Heatmap(
                        z=pivot.values,
                        x=[f"Wk {c}" for c in pivot.columns],
                        y=pivot.index.tolist(),
                        colorscale=[[0,"rgba(0,0,0,0)"],[0.01,"rgba(0,245,196,0.12)"],[1,accent]],
                        showscale=False,
                        text=[[f"{v:.1f}h" for v in row] for row in pivot.values],
                        texttemplate="%{text}", textfont=dict(size=10,color=t["text"]),
                        hovertemplate="<b>%{y}</b> · %{x}<br>%{text}<extra></extra>"
                    ))
                    fig_h.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=t["text2"],size=11,family="DM Sans"),
                        xaxis=dict(showgrid=False,side="top"),
                        yaxis=dict(showgrid=False),
                        margin=dict(l=0,r=0,t=0,b=0), height=200)
                    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar":False})
