import streamlit as st
from theme import get_theme
import database as db
import time
from datetime import datetime

SUBJECTS = ["FR","AFM","Audit","DT","IDT","IBS"]
SC = {"FR":"#7c3aed","AFM":"#2563eb","Audit":"#059669","DT":"#d97706","IDT":"#dc2626","IBS":"#0891b2"}

def render_lecture_library():
    t = get_theme()
    D = t["dark"]
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:24px;font-weight:800;color:{t['text']};">▶️ Lecture Library</div>
        <div style="font-size:13px;color:{t['text2']};margin-top:4px;">Track video lectures with live watch-time timer</div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📋  All Lectures", "➕  Add Lecture", "✅  Completed"])

    with tabs[0]:
        sub_filter = st.selectbox("Filter by Subject", ["All"]+SUBJECTS, key="lec_filter")
        q = "SELECT * FROM lectures WHERE status='Pending'" + (" AND subject=?" if sub_filter!="All" else "") + " ORDER BY id DESC"
        params = (sub_filter,) if sub_filter!="All" else ()
        df = db.fetch_data(q, params)

        if df.empty:
            st.success("🎉 All lectures watched! Check Completed tab.")
        else:
            st.markdown(f"**{len(df)} lecture(s) pending**")
            for _,row in df.iterrows():
                col_s = SC.get(row["subject"],"#6366f1")
                total_dur = float(row["total_duration"]) if float(row["total_duration"])>0 else 1.0
                watched   = float(row["watched_duration"])
                prog      = min(max(watched/total_dur,0.0),1.0)
                timer_key = f"timer_{row['id']}"
                start_key = f"start_{row['id']}"
                if timer_key not in st.session_state: st.session_state[timer_key]=False
                if start_key not in st.session_state: st.session_state[start_key]=0.0

                with st.container(border=True):
                    ha,hb = st.columns([3,1])
                    with ha:
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                            <span style="background:{col_s}22;color:{col_s};padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700;">{row["subject"]}</span>
                            <span style="font-size:14px;font-weight:700;color:{t['text']};">{row["lecture_name"]}</span>
                        </div>
                        <div style="font-size:12px;color:{t['text2']};margin-bottom:8px;">📖 {row["chapter"]} &nbsp;·&nbsp; ⏱ {int(total_dur)} min total</div>
                        """, unsafe_allow_html=True)
                        st.progress(prog, text=f"{int(watched)}/{int(total_dur)} min watched ({int(prog*100)}%)")
                    with hb:
                        if st.session_state[timer_key]:
                            elapsed_now = (time.time()-st.session_state[start_key])/60
                            st.markdown(f"""
                            <div style="background:#1e1b4b;border:1px solid #4f46e5;border-radius:10px;
                                 padding:10px;text-align:center;margin-bottom:8px;">
                                <div style="color:#a5b4fc;font-size:11px;">⏱ TRACKING</div>
                                <div style="color:{t['text']};font-weight:700;font-size:16px;">{elapsed_now:.1f} min</div>
                            </div>""", unsafe_allow_html=True)
                            if st.button("⏹ Stop & Save", key=f"stop_{row['id']}", use_container_width=True, type="primary"):
                                elapsed = (time.time()-st.session_state[start_key])/60
                                new_w = watched+elapsed
                                status = "Completed" if new_w>=(0.9*total_dur) else "Pending"
                                db.execute_query(
                                    "UPDATE lectures SET watched_duration=?,status=?,last_watched_date=? WHERE id=?",
                                    (new_w, status, datetime.now().strftime("%Y-%m-%d"), int(row["id"])))
                                db.execute_query(
                                    "INSERT INTO study_sessions (date,subject,category,duration_minutes) VALUES (?,?,'Lectures',?)",
                                    (datetime.now().strftime("%Y-%m-%d"), row["subject"], max(1,int(elapsed))))
                                st.session_state[timer_key]=False
                                st.session_state[start_key]=0.0
                                st.success(f"Saved {elapsed:.1f} min!")
                                st.rerun()
                        else:
                            if st.button("▶️ Start Watching", key=f"start_{row['id']}", use_container_width=True):
                                st.session_state[timer_key]=True
                                st.session_state[start_key]=time.time()
                                st.rerun()
                    if row["lecture_link"] and st.session_state[timer_key]:
                        try:
                            st.video(str(row["lecture_link"]))
                        except: pass

    with tabs[1]:
        with st.container(border=True):
            st.markdown("**Add New Lecture**")
            r1c1,r1c2 = st.columns(2)
            sub  = r1c1.selectbox("Subject",SUBJECTS,key="add_lec_sub")
            chap = r1c2.text_input("Chapter Name",key="add_lec_chap")
            name = st.text_input("Lecture Name / Title",key="add_lec_name")
            link = st.text_input("Video URL (YouTube / Google Drive)",key="add_lec_link",placeholder="https://...")
            dur  = st.number_input("Total Duration (minutes)",min_value=1.0,value=60.0,step=1.0,key="add_lec_dur")
            if st.button("💾 Add Lecture",type="primary",use_container_width=True):
                if name.strip() and chap.strip():
                    db.execute_query(
                        "INSERT INTO lectures (subject,chapter,lecture_name,lecture_link,total_duration) VALUES (?,?,?,?,?)",
                        (sub,chap.strip(),name.strip(),link.strip(),float(dur)))
                    st.success(f"✅ Added: **{name.strip()}**")
                    st.rerun()
                else:
                    st.error("Chapter and Lecture Name are required.")

    with tabs[2]:
        df_c = db.fetch_data("SELECT * FROM lectures WHERE status='Completed' ORDER BY last_watched_date DESC")
        if df_c.empty:
            st.info("No lectures completed yet.")
        else:
            st.markdown(f"**{len(df_c)} lecture(s) completed** 🎉")
            for _,row in df_c.iterrows():
                col_s = SC.get(row["subject"],"#6366f1")
                st.markdown(f"""
                <div style="padding:12px 16px;background:#052e16;border:1px solid #166534;border-radius:10px;margin-bottom:8px;
                     display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="color:{col_s};font-weight:700;font-size:12px;">{row["subject"]}</span>
                        <span style="color:{t['text']};font-size:13px;margin-left:8px;">{row["lecture_name"]}</span>
                        <div style="color:{t['text2']};font-size:11px;margin-top:2px;">{row["chapter"]}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:#22c55e;font-weight:700;font-size:13px;">✅ Done</div>
                        <div style="color:{t['text2']};font-size:11px;">{row["last_watched_date"] or ""}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
