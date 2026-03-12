import streamlit as st
from theme import get_theme
import database as db
from datetime import datetime

SC = {"FR":"#a78bfa","AFM":"#60a5fa","Audit":"#34d399","DT":"#fbbf24","IDT":"#f87171","IBS":"#38bdf8"}

def render_revision_schedule():
    t = get_theme()
    D = t["dark"]

    st.markdown(f"""
    <div style="margin-bottom:24px;">
      <div style="font-size:26px;font-weight:800;color:{t['text']};letter-spacing:-0.04em;">
        🔁 Revision Schedule</div>
      <div style="font-size:13px;color:{t['text2']};margin-top:4px;">
        Spaced repetition: Day +3, +7, +15, +30 after chapter completion</div>
    </div>""", unsafe_allow_html=True)

    today = datetime.now().strftime("%Y-%m-%d")
    df = db.fetch_data("""
        SELECT r.id as rev_id, s.subject, s.chapter,
               r.rev1_date, r.rev2_date, r.rev3_date, r.rev4_date,
               r.rev1_status, r.rev2_status, r.rev3_status, r.rev4_status
        FROM revisions r JOIN syllabus s ON r.chapter_id=s.id ORDER BY r.rev1_date DESC
    """)

    if df.empty:
        st.markdown(f"""
        <div style="text-align:center;padding:72px 0;">
          <div style="font-size:52px;margin-bottom:14px;opacity:0.4;">📅</div>
          <div style="font-size:17px;font-weight:700;color:{t['text']};margin-bottom:8px;">
            No revisions scheduled yet</div>
          <div style="font-size:13px;color:{t['text2']};">
            Go to <b>Syllabus &amp; Revisions</b> and mark chapters complete to auto-schedule.</div>
        </div>""", unsafe_allow_html=True)
        return

    today_c = overdue_c = upcoming_c = 0
    for _, row in df.iterrows():
        for n in [1,2,3,4]:
            if row[f"rev{n}_status"] == "Pending":
                d = row[f"rev{n}_date"]
                if d == today:    today_c   += 1
                elif d < today:   overdue_c  += 1
                else:             upcoming_c += 1

    st.markdown(f"""
    <div style="display:flex;gap:12px;margin-bottom:22px;">
      <div style="flex:1;background:{t['card']};border:1px solid rgba(248,113,113,0.35);
           border-radius:14px;padding:16px;text-align:center;">
        <div style="font-size:26px;font-weight:800;color:#f87171;
             font-family:'SF Mono','JetBrains Mono',monospace;">{overdue_c}</div>
        <div style="font-size:10px;color:{t['text2']};text-transform:uppercase;
             letter-spacing:1.5px;margin-top:3px;font-weight:700;">Overdue</div>
      </div>
      <div style="flex:1;background:{t['card']};border:1px solid rgba(251,191,36,0.35);
           border-radius:14px;padding:16px;text-align:center;">
        <div style="font-size:26px;font-weight:800;color:#fbbf24;
             font-family:'SF Mono','JetBrains Mono',monospace;">{today_c}</div>
        <div style="font-size:10px;color:{t['text2']};text-transform:uppercase;
             letter-spacing:1.5px;margin-top:3px;font-weight:700;">Due Today</div>
      </div>
      <div style="flex:1;background:{t['card']};border:1px solid rgba(52,211,153,0.35);
           border-radius:14px;padding:16px;text-align:center;">
        <div style="font-size:26px;font-weight:800;color:#34d399;
             font-family:'SF Mono','JetBrains Mono',monospace;">{upcoming_c}</div>
        <div style="font-size:10px;color:{t['text2']};text-transform:uppercase;
             letter-spacing:1.5px;margin-top:3px;font-weight:700;">Upcoming</div>
      </div>
    </div>""", unsafe_allow_html=True)

    filter_opt = st.radio("Show", ["All","Today","Overdue","Upcoming","Completed"],
                          horizontal=True, key="rev_filter")

    for _, row in df.iterrows():
        slots_to_show = []
        for n in [1,2,3,4]:
            d = row[f"rev{n}_date"]; st_s = row[f"rev{n}_status"]
            is_today = d == today and st_s == "Pending"
            is_over  = d <  today and st_s == "Pending"
            is_up    = d >  today and st_s == "Pending"
            is_done  = st_s == "Done"
            if   filter_opt == "All"       and not is_done: slots_to_show.append(n)
            elif filter_opt == "Today"     and is_today:    slots_to_show.append(n)
            elif filter_opt == "Overdue"   and is_over:     slots_to_show.append(n)
            elif filter_opt == "Upcoming"  and is_up:       slots_to_show.append(n)
            elif filter_opt == "Completed" and is_done:     slots_to_show.append(n)
        if not slots_to_show: continue

        sc = SC.get(str(row["subject"]), t["accent"])
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
              <span style="background:{sc}22;color:{sc};padding:3px 10px;
                   border-radius:20px;font-size:11px;font-weight:700;">{row['subject']}</span>
              <span style="font-size:14px;font-weight:600;color:{t['text']};">{row['chapter']}</span>
            </div>""", unsafe_allow_html=True)
            cols = st.columns(4)
            for i, n in enumerate([1,2,3,4]):
                d  = row[f"rev{n}_date"]; s = row[f"rev{n}_status"]
                is_done_s  = s == "Done"
                is_over_s  = d < today and s == "Pending"
                is_today_s = d == today and s == "Pending"
                bc    = "#34d399" if is_done_s else "#f87171" if is_over_s else "#fbbf24" if is_today_s else t["text3"]
                badge = "✅ Done" if is_done_s else "🔴 Overdue" if is_over_s else "🟡 Today" if is_today_s else "🔵 Soon"
                with cols[i]:
                    st.markdown(f"""
                    <div style="background:{t['bg']};border:1px solid {bc}44;
                         border-radius:10px;padding:10px;text-align:center;margin-bottom:6px;">
                      <div style="font-size:10px;color:{t['text3']};margin-bottom:4px;
                           font-weight:700;text-transform:uppercase;letter-spacing:1px;">REV {n}</div>
                      <div style="font-size:11px;font-weight:700;color:{bc};">{badge}</div>
                      <div style="font-size:11px;color:{t['text2']};margin-top:2px;">{d}</div>
                    </div>""", unsafe_allow_html=True)
                    if s == "Pending" and n in slots_to_show:
                        if st.button("Mark Done", key=f"rd_{row['rev_id']}_{n}", use_container_width=True):
                            db.execute_query(f"UPDATE revisions SET rev{n}_status='Done' WHERE id=?", (int(row["rev_id"]),))
                            st.rerun()
