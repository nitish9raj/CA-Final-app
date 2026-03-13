import streamlit as st
from theme import get_theme
import database as db
import icai_fetcher
from datetime import datetime

CAT_COLORS = {
    "RTP":           "#6366f1",
    "MTP":           "#0891b2",
    "Exam Paper":    "#059669",
    "Amendment":     "#dc2626",
    "Announcement":  "#f59e0b",
    "Study Material":"#7c3aed",
    "Guidance Note": "#d97706",
}
CAT_ICONS = {
    "RTP":           "📘",
    "MTP":           "📙",
    "Exam Paper":    "📄",
    "Amendment":     "⚠️",
    "Announcement":  "📢",
    "Study Material":"📚",
    "Guidance Note": "📋",
}
SUBJ_COLORS = {
    "FR":"#7c3aed","AFM":"#2563eb","Audit":"#059669",
    "DT":"#d97706","IDT":"#dc2626","IBS":"#0891b2","All":"#6366f1"
}

def render_icai_library():
    t = get_theme()
    D = t["dark"]
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-size:24px;font-weight:800;color:{t['text']};">🏛️ ICAI Resource Library</div>
        <div style="font-size:13px;color:{t["text2"]};margin-top:4px;">RTPs, MTPs, past papers, amendments & study material. Add or edit links anytime.</div>
    </div>""", unsafe_allow_html=True)

    # ── Init edit state
    if "icai_edit_id" not in st.session_state:
        st.session_state["icai_edit_id"] = None

    # ── Sync bar
    col_info, col_sync = st.columns([4, 1])
    df_count = db.fetch_data("SELECT COUNT(*) as c FROM icai_materials")
    n = int(df_count["c"].iloc[0]) if not df_count.empty else 0
    col_info.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};border-radius:10px;padding:12px 16px;display:flex;gap:24px;align-items:center;">
        <div><span style="font-size:20px;font-weight:800;color:#818cf8;">{n}</span>
             <span style="font-size:12px;color:{t["text2"]};margin-left:6px;">resources</span></div>
        <div style="font-size:12px;color:{t["text2"]};">Click <b style='color:#a5b4fc'>✏️ Edit Link</b> on any card to fix a broken URL</div>
    </div>""", unsafe_allow_html=True)
    with col_sync:
        if st.button("🔄 Sync Now", type="primary", use_container_width=True):
            with st.spinner("Loading resources..."):
                result = icai_fetcher.fetch_icai_announcements()
            st.success(f"✅ Done! ({result['added']} new items)")
            st.rerun()

    # Auto-seed on first load
    if n == 0:
        icai_fetcher.fetch_icai_announcements()
        st.rerun()

    # ── Add New Resource (always visible at top)
    with st.expander("➕ Add New Resource", expanded=False):
        st.markdown('<div style="font-size:13px;color:{t["text2"]};margin-bottom:10px;">Paste the correct ICAI link and fill in details.</div>', unsafe_allow_html=True)
        a1, a2, a3 = st.columns(3)
        new_title = st.text_input("Title / Description *", key="new_title",
                                   placeholder="e.g. RTP May 2026 — Paper 3: Advanced Auditing")
        new_link  = st.text_input("🔗 URL (paste exact link) *", key="new_link",
                                   placeholder="https://www.icai.org/...")
        new_cat   = a1.selectbox("Category", list(CAT_COLORS.keys()), key="new_cat")
        new_subj  = a2.selectbox("Subject",  ["All","FR","AFM","Audit","DT","IDT","IBS"], key="new_subj")
        if st.button("✅ Add Resource", type="primary", key="btn_add"):
            if new_title.strip() and new_link.strip():
                db.execute_query(
                    "INSERT INTO icai_materials (title,category,subject,link,fetch_date) VALUES (?,?,?,?,?)",
                    (new_title.strip(), new_cat, new_subj, new_link.strip(),
                     datetime.now().strftime("%Y-%m-%d")))
                st.success("✅ Resource added!")
                st.rerun()
            else:
                st.error("Both Title and URL are required.")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Edit modal (shown when edit button clicked)
    edit_id = st.session_state.get("icai_edit_id")
    if edit_id:
        row_df = db.fetch_data("SELECT * FROM icai_materials WHERE id=?", (edit_id,))
        if not row_df.empty:
            row = row_df.iloc[0]
            st.markdown(f"""
            <div style="background:#0c1a3a;border:2px solid #4f46e5;border-radius:14px;padding:16px 20px;margin-bottom:16px;">
                <div style="font-size:14px;font-weight:800;color:#a5b4fc;margin-bottom:12px;">
                    ✏️ Editing: <span style="color:{t['text']};">{row['title']}</span>
                </div>""", unsafe_allow_html=True)
            e1, e2, e3 = st.columns(3)
            e_title = st.text_input("Title", value=str(row["title"]), key="e_title")
            e_link  = st.text_input("🔗 URL (paste correct link here)", value=str(row["link"]), key="e_link",
                                     help="Copy the correct URL from ICAI website and paste here")
            e_cat   = e1.selectbox("Category", list(CAT_COLORS.keys()),
                                    index=list(CAT_COLORS.keys()).index(str(row["category"])) if str(row["category"]) in CAT_COLORS else 0,
                                    key="e_cat")
            e_subj  = e2.selectbox("Subject", ["All","FR","AFM","Audit","DT","IDT","IBS"],
                                    index=["All","FR","AFM","Audit","DT","IDT","IBS"].index(str(row["subject"])) if str(row["subject"]) in ["All","FR","AFM","Audit","DT","IDT","IBS"] else 0,
                                    key="e_subj")
            st.markdown('</div>', unsafe_allow_html=True)

            ec1, ec2, ec3 = st.columns([2, 2, 1])
            with ec1:
                if st.button("💾 Save Changes", type="primary", use_container_width=True):
                    db.execute_query(
                        "UPDATE icai_materials SET title=?,category=?,subject=?,link=? WHERE id=?",
                        (e_title.strip(), e_cat, e_subj, e_link.strip(), edit_id))
                    st.session_state["icai_edit_id"] = None
                    st.success("✅ Updated!")
                    st.rerun()
            with ec2:
                if st.button("🔗 Test Link", use_container_width=True):
                    st.markdown(f'<a href="{e_link}" target="_blank" style="color:#6366f1;">→ Open link in new tab</a>',
                                unsafe_allow_html=True)
            with ec3:
                if st.button("✖ Cancel", use_container_width=True):
                    st.session_state["icai_edit_id"] = None
                    st.rerun()

    # ── Load & filter
    df = db.fetch_data("SELECT * FROM icai_materials ORDER BY id DESC")
    if df.empty:
        st.info("No resources yet. Click 'Sync Now' or add one above.")
        return

    # Filters row
    f1, f2, f3 = st.columns([2, 2, 3])
    all_cats  = ["All"] + sorted(df["category"].unique().tolist())
    all_subjs = ["All"] + sorted(df["subject"].unique().tolist())
    cat_filter  = f1.selectbox("Category", all_cats,  key="icai_cat")
    subj_filter = f2.selectbox("Subject",  all_subjs, key="icai_subj")
    search_q    = f3.text_input("🔍 Search", key="icai_search", placeholder="Search title...")

    df_f = df.copy()
    if cat_filter  != "All": df_f = df_f[df_f["category"] == cat_filter]
    if subj_filter != "All": df_f = df_f[df_f["subject"]  == subj_filter]
    if search_q.strip():
        df_f = df_f[df_f["title"].str.contains(search_q.strip(), case=False, na=False)]

    __text2 = t["text2"]
    st.markdown(f"<div style='font-size:12px;color:{__text2};margin:8px 0;'>{len(df_f)} resource(s) shown</div>",
                unsafe_allow_html=True)

    # ── Tabs
    tabs = st.tabs(["📢 All", "📘 RTP / MTP", "📄 Exam Papers", "⚠️ Amendments", "📚 Study Material"])

    def _render_items(data):
        if data.empty:
            st.info("No items here. Click Sync Now or add manually above.")
            return
        for _, row in data.iterrows():
            rid    = int(row["id"])
            cat_c  = CAT_COLORS.get(str(row["category"]), "#6366f1")
            subj_c = SUBJ_COLORS.get(str(row["subject"]),  "#6366f1")
            icon   = CAT_ICONS.get(str(row["category"]),   "📄")
            link   = str(row["link"]) if row["link"] and str(row["link"]) != "nan" else "#"
            has_link = link != "#" and link.startswith("http")

            col_card, col_btns = st.columns([6, 1])
            with col_card:
                st.markdown(f"""
                <div style="background:{t['card']};border:1px solid {t['border']};border-radius:12px;
                     padding:14px 18px;border-left:3px solid {cat_c};margin-bottom:2px;">
                    <div style="display:flex;align-items:flex-start;gap:10px;">
                        <div style="flex:1;">
                            <div style="display:flex;gap:8px;margin-bottom:6px;flex-wrap:wrap;align-items:center;">
                                <span style="font-size:13px;">{icon}</span>
                                <span style="background:{cat_c}22;color:{cat_c};padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;text-transform:uppercase;">{row["category"]}</span>
                                <span style="background:{subj_c}22;color:{subj_c};padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;">{row["subject"]}</span>
                                {'<span style="background:#052e1622;color:#4ade80;padding:2px 8px;border-radius:10px;font-size:10px;">✓ has link</span>' if has_link else '<span style="background:#1f050522;color:#f87171;padding:2px 8px;border-radius:10px;font-size:10px;">⚠ no link</span>'}
                            </div>
                            <div style="font-size:13px;font-weight:600;color:{t['text']};margin-bottom:4px;">{row["title"]}</div>
                            <div style="font-size:11px;color:{t["text2"]};word-break:break-all;">
                                🔗 {link if has_link else "No URL set — click Edit Link to add"}
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_btns:
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                if has_link:
                    st.link_button("Open ↗", link, use_container_width=True)
                if st.button("✏️ Edit", key=f"edit_{rid}", use_container_width=True,
                             help="Fix or update the URL for this resource"):
                    st.session_state["icai_edit_id"] = rid
                    st.rerun()
                if st.button("🗑", key=f"del_{rid}", use_container_width=True,
                             help="Delete this resource"):
                    db.execute_query("DELETE FROM icai_materials WHERE id=?", (rid,))
                    st.rerun()

    with tabs[0]: _render_items(df_f)
    with tabs[1]: _render_items(df_f[df_f["category"].isin(["RTP","MTP"])])
    with tabs[2]: _render_items(df_f[df_f["category"].isin(["Exam Paper"])])
    with tabs[3]: _render_items(df_f[df_f["category"].isin(["Amendment","Announcement"])])
    with tabs[4]: _render_items(df_f[df_f["category"].isin(["Study Material","Guidance Note"])])
