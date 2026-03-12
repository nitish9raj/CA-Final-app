import streamlit as st
from theme import get_theme
import database as db
import plotly.graph_objects as go

SUBJECTS = ["FR","AFM","Audit","DT","IDT","IBS"]
SC = {"FR":"#7c3aed","AFM":"#2563eb","Audit":"#059669","DT":"#d97706","IDT":"#dc2626","IBS":"#0891b2"}
SOURCES = ["Past Exam","RTP","MTP","ICAI Study Material"]

def render_exam_mapping():
    t = get_theme()
    D = t["dark"]
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:24px;font-weight:800;color:{t['text']};">📋 Past Exam & RTP Mapping</div>
        <div style="font-size:13px;color:{t['text2']};margin-top:4px;">Map chapter appearances in past exams to find high-frequency topics</div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🔥  Frequency Analysis", "➕  Add Mapping", "📊  Heat Map"])

    with tabs[0]:
        freq_sub = st.selectbox("Subject", SUBJECTS, key="freq_sub")
        df = db.fetch_data(
            "SELECT chapter, source, year, status FROM chapter_questions WHERE subject=? ORDER BY chapter",
            (freq_sub,))
        df_freq = db.fetch_data(
            "SELECT chapter, COUNT(*) as frequency FROM chapter_questions WHERE subject=? GROUP BY chapter ORDER BY frequency DESC",
            (freq_sub,))

        if df_freq.empty:
            st.info(f"No mappings for **{freq_sub}** yet. Add them in the 'Add Mapping' tab.")
        else:
            col_s = SC.get(freq_sub,"#6366f1")
            st.markdown(f"**Top chapters by exam frequency — {freq_sub}**")
            max_f = int(df_freq["frequency"].max()) if not df_freq.empty else 1
            for _,row in df_freq.iterrows():
                f = int(row["frequency"])
                pct = round(f/max_f*100)
                st.markdown(f"""
                <div style="margin-bottom:10px;padding:12px 16px;background:{t['card']};border:1px solid {t['border']};
                     border-radius:10px;border-left:3px solid {col_s};">
                    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                        <span style="font-size:13px;font-weight:600;color:{t['text']};">{row["chapter"]}</span>
                        <span style="font-size:12px;font-weight:800;color:{col_s};">{f}x</span>
                    </div>
                    <div style="height:4px;background:{t['border']};border-radius:4px;overflow:hidden;">
                        <div style="height:100%;width:{pct}%;background:{col_s};border-radius:4px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

    with tabs[1]:
        with st.container(border=True):
            st.markdown("**Map a Chapter to a Past Paper**")
            c1,c2,c3 = st.columns(3)
            subject = c1.selectbox("Subject",SUBJECTS,key="map_sub")
            chapter = c2.text_input("Chapter Name",key="map_chap")
            source  = c3.selectbox("Source",SOURCES,key="map_src")
            year    = st.text_input("Year / Attempt",placeholder="e.g. Nov 2023, May 2024",key="map_year")
            if st.button("📌 Add Mapping",type="primary",use_container_width=True):
                if chapter.strip() and year.strip():
                    db.execute_query("INSERT INTO chapter_questions (subject,chapter,source,year) VALUES (?,?,?,?)",
                        (subject,chapter.strip(),source,year.strip()))
                    st.success(f"✅ Mapped: **{chapter.strip()}** → {source} ({year})")
                    st.rerun()
                else:
                    st.error("Chapter and Year/Attempt are required.")

        # Recent mappings
        df_rec = db.fetch_data("SELECT subject,chapter,source,year FROM chapter_questions ORDER BY id DESC LIMIT 20")
        if not df_rec.empty:
            st.markdown("**Recent Mappings**")
            st.dataframe(df_rec,use_container_width=True,hide_index=True)

    with tabs[2]:
        st.markdown("**Exam Frequency Heat Map — All Subjects**")
        df_all = db.fetch_data(
            "SELECT subject, chapter, COUNT(*) as freq FROM chapter_questions GROUP BY subject, chapter ORDER BY freq DESC")
        if df_all.empty:
            st.info("Add mappings to see the heat map.")
        else:
            for sub in SUBJECTS:
                df_s = df_all[df_all["subject"]==sub].head(8)
                if df_s.empty: continue
                col_s = SC.get(sub,"#6366f1")
                st.markdown(f"**{sub}**")
                cols = st.columns(min(4,len(df_s)))
                for i,(_,row) in enumerate(df_s.iterrows()):
                    intensity = min(int(row["freq"]*30),255)
                    with cols[i%4]:
                        st.markdown(f"""
                        <div style="background:{col_s}{hex(intensity)[2:].zfill(2)};border:1px solid {col_s}44;
                             border-radius:8px;padding:8px;text-align:center;margin-bottom:8px;">
                            <div style="font-size:11px;color:{t['text']};font-weight:600;">{row["chapter"][:20]}{'…' if len(str(row["chapter"]))>20 else ''}</div>
                            <div style="font-size:16px;font-weight:800;color:{t['text']};">{int(row["freq"])}x</div>
                        </div>""", unsafe_allow_html=True)
