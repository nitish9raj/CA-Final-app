import streamlit as st
import database as db
from datetime import datetime, timedelta
import plotly.graph_objects as go
from theme import get_theme

SC = {"FR":"#a78bfa","AFM":"#60a5fa","Audit":"#34d399","DT":"#fbbf24","IDT":"#f87171","IBS":"#38bdf8"}

def kpi(label, value, sub, color, icon):
    t = get_theme()
    D = t["dark"]
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-radius:18px;padding:22px 20px 18px;
         box-shadow:0 2px 12px {t['shadow']};
         transition:transform .2s,box-shadow .2s;position:relative;overflow:hidden;"
         onmouseenter="this.style.transform='translateY(-3px)';this.style.boxShadow='0 12px 32px {t['shadow']}'"
         onmouseleave="this.style.transform='';this.style.boxShadow='0 2px 12px {t['shadow']}'">
      <div style="position:absolute;top:0;left:0;right:0;height:3px;
           background:linear-gradient(90deg,{color},transparent);border-radius:18px 18px 0 0;"></div>
      <div style="position:absolute;top:14px;right:16px;font-size:22px;opacity:0.18;">{icon}</div>
      <div style="font-size:9px;color:{t['text3']};text-transform:uppercase;
           letter-spacing:2px;margin-bottom:10px;font-weight:700;">{label}</div>
      <div style="font-size:28px;font-weight:700;color:{t['text']};
           font-family:'SF Mono','JetBrains Mono',monospace;
           letter-spacing:-0.05em;line-height:1;">{value}</div>
      <div style="font-size:11px;color:{color};margin-top:8px;font-weight:600;">{sub}</div>
    </div>""", unsafe_allow_html=True)

def render_dashboard():
    t = get_theme()
    D = t["dark"]

    exam_str  = st.session_state.get("exam_date","2026-05-01")
    try: days_left = max(0,(datetime.strptime(exam_str,"%Y-%m-%d")-datetime.now()).days)
    except: days_left = 0

    today = datetime.now().strftime("%Y-%m-%d")
    hour  = datetime.now().hour
    greet = "Good Morning 🌅" if hour<12 else "Good Afternoon ☀️" if hour<17 else "Good Evening 🌙"

    # ── Data queries using correct column names ──────────────
    df_t   = db.fetch_data("SELECT duration_minutes FROM study_sessions WHERE date=?",(today,))
    t_min  = int(df_t["duration_minutes"].sum()) if not df_t.empty else 0
    df_s   = db.fetch_data("SELECT status FROM syllabus")
    tot_c  = len(df_s)
    don_c  = int((df_s["status"]=="Completed").sum()) if not df_s.empty else 0
    df_a   = db.fetch_data("SELECT duration_minutes FROM study_sessions")
    t_all  = int(df_a["duration_minutes"].sum()) if not df_a.empty else 0
    df_lec = db.fetch_data("SELECT status FROM lectures")
    don_l  = int((df_lec["status"]=="Completed").sum()) if not df_lec.empty else 0
    tot_l  = len(df_lec)
    df_pq  = db.fetch_data("SELECT status FROM practice_questions")
    pen_pq = int((df_pq["status"]=="Pending").sum()) if not df_pq.empty else 0
    prep   = round(don_c/tot_c*100) if tot_c>0 else 0
    clr_d  = "#f87171" if days_left<30 else "#fbbf24" if days_left<60 else t["accent"]

    # ── Hero ─────────────────────────────────────────────────
    if D:
        hero_bg = "linear-gradient(135deg,#111120 0%,#16162a 60%,#1a1235 100%)"
        glow    = "radial-gradient(ellipse 55% 100% at 90% 50%,rgba(124,111,247,0.14),transparent)"
    else:
        hero_bg = "linear-gradient(135deg,#ffffff 0%,#f5f3ff 60%,#ede9ff 100%)"
        glow    = "radial-gradient(ellipse 55% 100% at 90% 50%,rgba(91,80,232,0.09),transparent)"

    st.markdown(f"""
    <div style="position:relative;overflow:hidden;background:{hero_bg};
         border:1px solid {t['border']};border-radius:24px;
         padding:30px 36px 28px;margin-bottom:28px;
         box-shadow:0 4px 28px {t['shadow']};">
      <div style="position:absolute;inset:0;background:{glow};pointer-events:none;"></div>
      <div style="position:absolute;left:0;top:15%;bottom:15%;width:4px;
           background:linear-gradient(180deg,{t['accent']} 0%,{t['accent2']} 100%);
           border-radius:0 4px 4px 0;"></div>
      <div style="position:absolute;right:-20px;top:-20px;width:140px;height:140px;
           border-radius:50%;background:{"rgba(124,111,247,0.06)" if D else "rgba(91,80,232,0.05)"};
           pointer-events:none;"></div>

      <div style="font-size:26px;font-weight:800;color:{t['text']};
           letter-spacing:-0.04em;line-height:1.2;position:relative;">{greet}</div>
      <div style="font-size:13px;color:{t['text2']};margin-top:7px;font-weight:400;position:relative;">
        {datetime.now().strftime("%A, %d %B %Y")}
        <span style="color:{t['text3']};margin:0 8px;">·</span>
        CA Final in <span style="color:{clr_d};font-weight:700;">{days_left} days</span>
      </div>
      <div style="margin-top:20px;display:flex;align-items:center;gap:14px;position:relative;">
        <div style="flex:1;height:6px;
             background:{"rgba(255,255,255,0.07)" if D else "rgba(0,0,0,0.07)"};
             border-radius:999px;overflow:hidden;">
          <div style="height:100%;width:{prep}%;
               background:linear-gradient(90deg,{t['accent']},{t['accent2']});
               border-radius:999px;transition:width .7s cubic-bezier(.4,0,.2,1);"></div>
        </div>
        <div style="font-size:13px;color:{t['text2']};font-weight:600;white-space:nowrap;">
          {prep}% <span style="color:{t['text3']};font-weight:400;">syllabus done</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── KPIs ─────────────────────────────────────────────────
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("Today's Study",  f"{t_min//60}h {t_min%60}m", f"{t_min} min today",   t["accent"],  "⏱")
    with c2: kpi("All-Time Hours", f"{t_all//60}h",              f"{t_all} min total",   "#34d399",    "📚")
    with c3: kpi("Syllabus Done",  f"{don_c}/{tot_c}",           f"{prep}% complete",    "#fbbf24",    "✅")
    with c4: kpi("Lectures Done",  f"{don_l}/{tot_l}",           "video progress",       "#f472b6",    "▶️")
    with c5: kpi("Practice Queue", str(pen_pq),                  "questions pending",    "#38bdf8",    "📝")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Charts ───────────────────────────────────────────────
    col_chart, col_subj = st.columns([3,2])

    with col_chart:
        with st.container(border=True):
            st.markdown(f"""
            <div style="font-size:14px;font-weight:700;color:{t['text']};
                 letter-spacing:-0.02em;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
              <span style="background:{"rgba(124,111,247,0.15)" if D else "rgba(91,80,232,0.1)"};
                   padding:4px 8px;border-radius:8px;font-size:16px;">📈</span>
              Study Hours — Last 14 Days
            </div>""", unsafe_allow_html=True)

            dates  = [(datetime.now()-timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13,-1,-1)]
            labels = [(datetime.now()-timedelta(days=i)).strftime("%d %b")    for i in range(13,-1,-1)]
            hours  = []
            for d in dates:
                df_d = db.fetch_data("SELECT duration_minutes FROM study_sessions WHERE date=?",(d,))
                hours.append(round(df_d["duration_minutes"].sum()/60,1) if not df_d.empty else 0)

            if sum(hours)==0:
                st.markdown(f"""
                <div style="background:{t['bg']};border:1px solid {t['border']};border-radius:14px;
                     padding:48px 20px;text-align:center;">
                  <div style="font-size:40px;margin-bottom:12px;opacity:0.4;">📊</div>
                  <div style="font-size:14px;font-weight:600;color:{t['text2']};">No sessions logged yet</div>
                  <div style="font-size:12px;color:{t['text3']};margin-top:4px;">
                    Add your first study session to see the chart
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                colors = [t["accent"] if h>0 else t["border"] for h in hours]
                fig = go.Figure(go.Bar(x=labels, y=hours, marker=dict(
                    color=colors, line=dict(width=0), cornerradius=6),
                    hovertemplate='<b>%{x}</b><br>%{y:.1f}h<extra></extra>'))
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter,sans-serif", color=t["text2"], size=11),
                    xaxis=dict(showgrid=False, tickfont=dict(size=10), linecolor=t["border"]),
                    yaxis=dict(showgrid=True, gridcolor=t["border"], zeroline=False, tickfont=dict(size=10)),
                    margin=dict(l=0,r=0,t=4,b=0), height=215, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with col_subj:
        with st.container(border=True):
            st.markdown(f"""
            <div style="font-size:14px;font-weight:700;color:{t['text']};
                 letter-spacing:-0.02em;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
              <span style="background:{"rgba(124,111,247,0.15)" if D else "rgba(91,80,232,0.1)"};
                   padding:4px 8px;border-radius:8px;font-size:16px;">🎯</span>
              Subject Progress
            </div>""", unsafe_allow_html=True)
            for subj, clr in SC.items():
                df_sub = db.fetch_data("SELECT status FROM syllabus WHERE subject=?",(subj,))
                total  = len(df_sub)
                done   = int((df_sub["status"]=="Completed").sum()) if not df_sub.empty else 0
                pct    = round(done/total*100) if total>0 else 0
                st.markdown(f"""
                <div style="margin-bottom:13px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                    <span style="font-size:12px;font-weight:600;color:{t['text2']};">{subj}</span>
                    <span style="font-size:10px;color:{clr};font-weight:700;
                         background:{"rgba(255,255,255,0.06)" if D else "rgba(0,0,0,0.06)"};
                         padding:2px 9px;border-radius:20px;">{pct}%</span>
                  </div>
                  <div style="height:5px;background:{t['bg3']};border-radius:999px;overflow:hidden;">
                    <div style="height:100%;width:{pct}%;background:{clr};
                         border-radius:999px;transition:width .6s cubic-bezier(.4,0,.2,1);"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Revisions + Recent — correct DB columns ───────────────
    col_rev, col_act = st.columns(2)

    with col_rev:
        with st.container(border=True):
            st.markdown(f"""
            <div style="font-size:14px;font-weight:700;color:{t['text']};
                 letter-spacing:-0.02em;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
              <span style="background:{"rgba(124,111,247,0.15)" if D else "rgba(91,80,232,0.1)"};
                   padding:4px 8px;border-radius:8px;">🔁</span> Upcoming Revisions
            </div>""", unsafe_allow_html=True)
            # revisions table: chapter_id → join syllabus for chapter name + subject
            # Use rev1_date as next_revision proxy
            df_rev = db.fetch_data("""
                SELECT s.chapter, s.subject, r.rev1_date
                FROM revisions r
                JOIN syllabus s ON s.id = r.chapter_id
                WHERE r.rev1_status='Pending'
                ORDER BY r.rev1_date
                LIMIT 6
            """)
            if df_rev.empty:
                st.markdown(f"""
                <div style="padding:24px;text-align:center;">
                  <div style="font-size:32px;margin-bottom:8px;">🎉</div>
                  <div style="font-size:13px;color:{t['text2']};">No revisions due soon</div>
                </div>""", unsafe_allow_html=True)
            else:
                for _, row in df_rev.iterrows():
                    clr2 = SC.get(str(row.get("subject","")), t["accent"])
                    due  = str(row.get("rev1_date",""))
                    over = due and due < datetime.now().strftime("%Y-%m-%d")
                    bc   = "#f87171" if over else t["accent"]
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                         padding:10px 0;border-bottom:1px solid {t['border']};">
                      <div style="flex:1;min-width:0;">
                        <div style="font-size:12px;font-weight:600;color:{t['text']};
                             white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                             max-width:180px;">{row.get('chapter','')}</div>
                        <div style="font-size:10px;color:{clr2};margin-top:2px;font-weight:600;">
                          {row.get('subject','')}</div>
                      </div>
                      <div style="font-size:10px;color:{bc};font-weight:700;
                           background:{"rgba(248,113,113,0.1)" if over else "rgba(124,111,247,0.1)"};
                           padding:3px 9px;border-radius:8px;white-space:nowrap;margin-left:8px;">
                        {"⚠ " if over else ""}{due}
                      </div>
                    </div>""", unsafe_allow_html=True)

    with col_act:
        with st.container(border=True):
            st.markdown(f"""
            <div style="font-size:14px;font-weight:700;color:{t['text']};
                 letter-spacing:-0.02em;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
              <span style="background:{"rgba(124,111,247,0.15)" if D else "rgba(91,80,232,0.1)"};
                   padding:4px 8px;border-radius:8px;">⏱️</span> Recent Sessions
            </div>""", unsafe_allow_html=True)
            # study_sessions has: id, date, subject, category, duration_minutes
            df_rec = db.fetch_data(
                "SELECT date, subject, category, duration_minutes FROM study_sessions ORDER BY id DESC LIMIT 6")
            if df_rec.empty:
                st.markdown(f"""
                <div style="padding:24px;text-align:center;">
                  <div style="font-size:32px;margin-bottom:8px;">⏱️</div>
                  <div style="font-size:13px;color:{t['text2']};">No sessions logged yet</div>
                </div>""", unsafe_allow_html=True)
            else:
                for _, row in df_rec.iterrows():
                    clr2 = SC.get(str(row.get("subject","")), t["accent"])
                    dur  = int(row.get("duration_minutes",0))
                    cat  = str(row.get("category",""))
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                         padding:10px 0;border-bottom:1px solid {t['border']};">
                      <div>
                        <div style="font-size:12px;font-weight:600;color:{t['text']};">
                          {row.get('subject','General')}</div>
                        <div style="font-size:10px;color:{t['text3']};margin-top:2px;">
                          {row.get('date','')}
                          {f" · {cat}" if cat else ""}
                        </div>
                      </div>
                      <div style="font-size:12px;color:{clr2};font-weight:700;
                           background:{"rgba(124,111,247,0.1)" if D else "rgba(91,80,232,0.07)"};
                           padding:4px 12px;border-radius:10px;
                           font-family:'SF Mono','JetBrains Mono',monospace;letter-spacing:-0.02em;">
                        {dur//60}h {dur%60}m
                      </div>
                    </div>""", unsafe_allow_html=True)
