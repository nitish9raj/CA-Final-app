import streamlit as st
from theme import get_theme
import database as db
from datetime import datetime
from revision_engine import schedule_chapter_revision

SUBJECTS = ["FR","AFM","Audit","DT","IDT","IBS"]
SUBJECT_FULL = {"FR":"Financial Reporting","AFM":"Advanced Financial Management",
    "Audit":"Auditing & Ethics","DT":"Direct Tax","IDT":"Indirect Tax","IBS":"Integrated Business Solutions"}
SUBJECT_COLORS = {"FR":"#7c3aed","AFM":"#2563eb","Audit":"#059669","DT":"#d97706","IDT":"#dc2626","IBS":"#0891b2"}
W_COLOR = {"High":"#ef4444","Medium":"#f59e0b","Low":"#22c55e"}

def render_syllabus_tracker():
    t = get_theme()
    D = t["dark"]
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:24px;font-weight:800;color:{t['text']};">📚 Syllabus & Revision Tracker</div>
        <div style="font-size:13px;color:{t['text2']};margin-top:4px;">Manage chapters and auto-schedule spaced repetition</div>
    </div>""", unsafe_allow_html=True)

    # Subject selector as styled pills
    subject = st.selectbox("Subject", SUBJECTS,
        format_func=lambda s: f"{s}  ·  {SUBJECT_FULL[s]}", key="syl_sub")
    color = SUBJECT_COLORS.get(subject,"#6366f1")

    # Add chapter
    with st.container(border=True):
        st.markdown("**➕ Add New Chapter**")
        c1,c2,c3 = st.columns([3,1,1])
        new_ch = c1.text_input("Chapter Name", placeholder="e.g. Ind AS 115 — Revenue from Contracts", key="new_ch", label_visibility="collapsed")
        wt = c2.selectbox("Weightage", ["High","Medium","Low"], key="new_wt", label_visibility="collapsed")
        c3.write("")
        if c3.button("Add Chapter", type="primary", use_container_width=True):
            if new_ch.strip():
                db.execute_query("INSERT INTO syllabus (subject,chapter,status,weightage) VALUES (?,?,'Pending',?)",
                    (subject, new_ch.strip(), wt))
                st.success(f"✅ Added: **{new_ch.strip()}**")
                st.rerun()
            else:
                st.error("Chapter name cannot be empty.")

    df = db.fetch_data("SELECT id,chapter,status,weightage FROM syllabus WHERE subject=? ORDER BY id",(subject,))

    if df.empty:
        st.markdown(f"""
        <div style="text-align:center;padding:48px 0;color:{t['text3']};">
            <div style="font-size:32px;margin-bottom:8px;">📭</div>
            <div style="font-size:14px;">No chapters added for <b style="color:{color};">{subject}</b> yet.</div>
        </div>""", unsafe_allow_html=True)
        return

    pending = df[df["status"]=="Pending"]
    completed = df[df["status"]=="Completed"]
    prog = len(completed)/len(df) if len(df)>0 else 0

    # Progress header
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {color}44;
         border-left:4px solid {color};border-radius:12px;padding:16px 20px;margin:16px 0;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <div style="font-size:15px;font-weight:700;color:{t['text']};">{subject} — {SUBJECT_FULL[subject]}</div>
            <div style="font-size:20px;font-weight:800;color:{color};">{int(prog*100)}%</div>
        </div>
        <div style="height:6px;background:{t['border']};border-radius:4px;overflow:hidden;">
            <div style="height:100%;width:{int(prog*100)}%;background:{color};border-radius:4px;transition:width .5s;"></div>
        </div>
        <div style="font-size:12px;color:{t['text2']};margin-top:6px;">{len(completed)} of {len(df)} chapters completed</div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs([f"⏳  Pending ({len(pending)})", f"✅  Completed ({len(completed)})", "📊  Overview"])

    with tabs[0]:
        if pending.empty:
            st.success(f"🎉 All chapters completed for {subject}!")
        else:
            for _,row in pending.iterrows():
                wt_col = W_COLOR.get(row["weightage"],"#94a3b8")
                col_a,col_b,col_c,col_d = st.columns([5,1,1,1])
                col_a.markdown(f"**{row['chapter']}**")
                col_b.markdown(f"<span style='color:{wt_col};font-size:12px;font-weight:700;'>{'●'} {row['weightage']}</span>", unsafe_allow_html=True)
                col_c.markdown("<span style='color:#f59e0b;font-size:12px;'>⏳ Pending</span>", unsafe_allow_html=True)
                if col_d.button("✅ Done", key=f"done_{row['id']}", use_container_width=True):
                    db.execute_query("UPDATE syllabus SET status='Completed' WHERE id=?",(row["id"],))
                    schedule_chapter_revision(row["id"], datetime.now().strftime("%Y-%m-%d"))
                    st.success(f"✅ '{row['chapter']}' done! Revision scheduled at +3, +7, +15, +30 days 🗓️")
                    st.rerun()

    with tabs[1]:
        if completed.empty:
            st.info("No chapters completed yet.")
        else:
            for _,row in completed.iterrows():
                col_a,col_b,col_c,col_d = st.columns([5,1,1,1])
                col_a.markdown(f"~~{row['chapter']}~~")
                col_b.markdown(f"<span style='color:{W_COLOR.get(row['weightage'],'#94a3b8')};font-size:12px;'>{'●'} {row['weightage']}</span>", unsafe_allow_html=True)
                col_c.markdown("<span style='color:#22c55e;font-size:12px;'>✅ Done</span>", unsafe_allow_html=True)
                if col_d.button("↩️", key=f"undo_{row['id']}", help="Undo completion"):
                    db.execute_query("UPDATE syllabus SET status='Pending' WHERE id=?",(row["id"],))
                    db.execute_query("DELETE FROM revisions WHERE chapter_id=?",(row["id"],))
                    st.rerun()

    with tabs[2]:
        # All subjects overview
        st.markdown("**All Subjects Progress**")
        for s in SUBJECTS:
            df_s = db.fetch_data("SELECT status FROM syllabus WHERE subject=?",(s,))
            total_s = len(df_s)
            done_s = int((df_s["status"]=="Completed").sum()) if not df_s.empty else 0
            p = done_s/total_s if total_s>0 else 0
            sc = SUBJECT_COLORS.get(s,"#6366f1")
            st.markdown(f"""
            <div style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:13px;font-weight:600;color:{t['text']};">{s} <span style="color:{t['text2']};font-weight:400;font-size:12px;">— {SUBJECT_FULL[s]}</span></span>
                    <span style="font-size:12px;color:{sc};font-weight:700;">{done_s}/{total_s}</span>
                </div>
                <div style="height:5px;background:{t['border']};border-radius:4px;overflow:hidden;">
                    <div style="height:100%;width:{int(p*100)}%;background:{sc};border-radius:4px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
