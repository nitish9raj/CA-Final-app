import streamlit as st
from theme import get_theme
import database as db
from datetime import datetime

SUBJECTS = ["FR","AFM","Audit","DT","IDT","IBS"]
SC = {"FR":"#7c3aed","AFM":"#2563eb","Audit":"#059669","DT":"#d97706","IDT":"#dc2626","IBS":"#0891b2"}
SOURCES = ["Past Exam","RTP","MTP","ICAI Study Material","Conceptual"]

def render_practice_generator():
    t = get_theme()
    D = t["dark"]
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:24px;font-weight:800;color:{t['text']};">📝 Practice Questions</div>
        <div style="font-size:13px;color:{t['text2']};margin-top:4px;">Generate and track chapter-wise practice sets</div>
    </div>""", unsafe_allow_html=True)

    # Stats bar
    df_all  = db.fetch_data("SELECT status FROM practice_questions")
    pending = int((df_all["status"]=="Pending").sum()) if not df_all.empty else 0
    solved  = int((df_all["status"]=="Solved").sum())  if not df_all.empty else 0
    total   = len(df_all)
    pct     = round(solved/total*100) if total>0 else 0

    st.markdown(f"""
    <div style="display:flex;gap:12px;margin-bottom:20px;">
        <div style="flex:1;background:{t['card']};border:1px solid #6366f144;border-radius:12px;padding:14px;text-align:center;">
            <div style="font-size:22px;font-weight:800;color:#818cf8;">{total}</div>
            <div style="font-size:11px;color:{t['text2']};text-transform:uppercase;letter-spacing:1px;">Total</div>
        </div>
        <div style="flex:1;background:{t['card']};border:1px solid #f59e0b44;border-radius:12px;padding:14px;text-align:center;">
            <div style="font-size:22px;font-weight:800;color:#f59e0b;">{pending}</div>
            <div style="font-size:11px;color:{t['text2']};text-transform:uppercase;letter-spacing:1px;">Pending</div>
        </div>
        <div style="flex:1;background:{t['card']};border:1px solid #22c55e44;border-radius:12px;padding:14px;text-align:center;">
            <div style="font-size:22px;font-weight:800;color:#22c55e;">{solved}</div>
            <div style="font-size:11px;color:{t['text2']};text-transform:uppercase;letter-spacing:1px;">Solved · {pct}%</div>
        </div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🎯  Practice Queue", "➕  Generate Set", "📊  Analytics"])

    with tabs[0]:
        sub_f = st.selectbox("Filter by Subject", ["All"]+SUBJECTS, key="pq_filter")
        df = db.fetch_data(
            "SELECT * FROM practice_questions WHERE status='Pending'" +
            (" AND subject=?" if sub_f!="All" else "") + " ORDER BY id",
            (sub_f,) if sub_f!="All" else ())

        if df.empty:
            st.success("🎉 No pending practice questions!")
        else:
            for _,row in df.iterrows():
                col_s = SC.get(row["subject"],"#6366f1")
                ca,cb,cc = st.columns([4,1,1])
                ca.markdown(f"""
                <div style="padding:10px 0;">
                    <span style="background:{col_s}22;color:{col_s};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;">{row["subject"]}</span>
                    <span style="color:{t['text']};font-size:13px;font-weight:600;margin-left:8px;">{row["chapter"]}</span>
                    <span style="color:{t['text2']};font-size:11px;margin-left:6px;">· {row["source"]}</span>
                </div>""", unsafe_allow_html=True)
                if cb.button("✅ Solved", key=f"sv_{row['id']}", use_container_width=True, type="primary"):
                    db.execute_query("UPDATE practice_questions SET status='Solved' WHERE id=?",(int(row["id"]),))
                    st.rerun()
                if cc.button("🗑", key=f"dl_{row['id']}", use_container_width=True):
                    db.execute_query("DELETE FROM practice_questions WHERE id=?",(int(row["id"]),))
                    st.rerun()

    with tabs[1]:
        with st.container(border=True):
            st.markdown("**Generate a Practice Set for a Chapter**")
            gc1,gc2 = st.columns(2)
            g_sub  = gc1.selectbox("Subject",SUBJECTS,key="gen_sub")
            g_chap = gc2.text_input("Chapter Name",key="gen_chap",placeholder="e.g. Ind AS 115")
            g_src  = st.multiselect("Include Sources",SOURCES,default=["Past Exam","RTP","Conceptual"],key="gen_src")
            if st.button("⚡ Generate Practice Set",type="primary",use_container_width=True):
                if g_chap.strip() and g_src:
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    for src in g_src:
                        db.execute_query(
                            "INSERT INTO practice_questions (subject,chapter,source,generated_date) VALUES (?,?,?,?)",
                            (g_sub,g_chap.strip(),src,today_str))
                    st.success(f"✅ Generated {len(g_src)} practice cards for **{g_chap.strip()}**!")
                    st.rerun()
                else:
                    st.error("Enter chapter name and select at least one source.")

        # Quick add single
        st.divider()
        st.markdown("**Add Single Question**")
        qa,qb,qc = st.columns(3)
        qs_sub  = qa.selectbox("Subject",SUBJECTS,key="qs_sub")
        qs_chap = qb.text_input("Chapter",key="qs_chap")
        qs_src  = qc.selectbox("Source",SOURCES,key="qs_src")
        if st.button("Add",key="add_single_q"):
            if qs_chap.strip():
                db.execute_query("INSERT INTO practice_questions (subject,chapter,source,generated_date) VALUES (?,?,?,?)",
                    (qs_sub,qs_chap.strip(),qs_src,datetime.now().strftime("%Y-%m-%d")))
                st.success("Added!")
                st.rerun()

    with tabs[2]:
        df_a = db.fetch_data("""SELECT subject,
            SUM(CASE WHEN status='Solved' THEN 1 ELSE 0 END) as solved,
            COUNT(*) as total FROM practice_questions GROUP BY subject""")
        if df_a.empty:
            st.info("No data yet.")
        else:
            for _,row in df_a.iterrows():
                p = round(row["solved"]/row["total"]*100) if row["total"]>0 else 0
                col_s = SC.get(row["subject"],"#6366f1")
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                        <span style="font-size:13px;font-weight:600;color:{t['text']};">{row["subject"]}</span>
                        <span style="font-size:12px;color:{col_s};font-weight:700;">{int(row["solved"])}/{int(row["total"])} · {p}%</span>
                    </div>
                    <div style="height:6px;background:{t['border']};border-radius:4px;overflow:hidden;">
                        <div style="height:100%;width:{p}%;background:{col_s};border-radius:4px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
