import streamlit as st
import file_reader
import ai_quiz_engine
import database as db
from datetime import datetime
import re
from theme import get_theme

SUBJECTS = ["FR","AFM","Audit","DT","IDT","IBS","General"]
SC = {"FR":"#7c3aed","AFM":"#2563eb","Audit":"#059669","DT":"#d97706","IDT":"#dc2626","IBS":"#0891b2","General":"#6366f1"}

def _badge(text, color):
    return f'<span style="background:{color}22;color:{color};padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;">{text}</span>'

def _section(title, sub=""):
    t = get_theme()
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <div style="font-size:15px;font-weight:700;color:{t['text']};">{title}</div>
        __text2 = t["text2"]
        {f'<div style="font-size:12px;color:{__text2};">{sub}</div>' if sub else ""}
    </div>""", unsafe_allow_html=True)

def _card_bg(dark_col, light_col):
    """Return theme-appropriate card background color."""
    t = get_theme()
    return dark_col if t["dark"] else light_col

def _render_rich_summary(summary, filename):
    t = get_theme()
    D = t["dark"]
    col_s = SC.get(summary["topic"].upper(), "#6366f1")
    subj_name = summary["subject_name"]
    card_bg  = t["bg2"]
    card_bdr = t["border2"]
    txt      = t["text"]
    txt2     = t["text2"]
    txt3     = t["text3"]

    st.markdown(f"""
    <div style="background:{card_bg};border:1px solid {col_s}44;
         border-radius:14px;padding:18px 22px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="font-size:11px;color:{txt2};text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">Document Analyzed</div>
                <div style="font-size:16px;font-weight:700;color:{txt};">📎 {filename}</div>
                <div style="margin-top:8px;">{_badge(subj_name, col_s)}</div>
            </div>
            <div style="display:flex;gap:20px;flex-wrap:wrap;">
                <div style="text-align:center;">
                    <div style="font-size:22px;font-weight:800;color:{col_s};font-family:'JetBrains Mono',monospace;">{summary['word_count']:,}</div>
                    <div style="font-size:10px;color:{txt2};text-transform:uppercase;">words</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:22px;font-weight:800;color:#818cf8;font-family:'JetBrains Mono',monospace;">{summary['para_count']}</div>
                    <div style="font-size:10px;color:{txt2};text-transform:uppercase;">paragraphs</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:22px;font-weight:800;color:#34d399;font-family:'JetBrains Mono',monospace;">{len(summary['headings'])}</div>
                    <div style="font-size:10px;color:{txt2};text-transform:uppercase;">sections</div>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    if summary.get("headings"):
        with st.expander("📑 Document Structure"):
            for h in summary["headings"][:12]:
                depth = h.get("depth",1)
                indent = (depth-1)*16
                _fsize = "14" if depth==1 else "12"
                _fwgt  = "700" if depth==1 else "500"
                _bullet = "▪" if depth==1 else "–"
                _htext  = h["text"]
                st.markdown(f'<div style="padding:4px 0 4px {indent}px;color:{txt};font-size:{_fsize}px;font-weight:{_fwgt};">{_bullet} {_htext}</div>', unsafe_allow_html=True)

    if summary.get("key_concepts"):
        st.markdown(f"<div style='font-size:13px;font-weight:700;color:{txt};margin:14px 0 8px;'>🔑 Key Concepts</div>", unsafe_allow_html=True)
        chip_html = " ".join(f'<span style="display:inline-block;background:{col_s}18;color:{col_s};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;margin:3px 2px;">{c}</span>' for c in summary["key_concepts"][:16])
        st.markdown(f"<div>{chip_html}</div>", unsafe_allow_html=True)

    if summary.get("summary_points"):
        st.markdown(f"<div style='font-size:13px;font-weight:700;color:{txt};margin:14px 0 8px;'>📝 Key Points</div>", unsafe_allow_html=True)
        for pt in summary["summary_points"][:8]:
            st.markdown(f"""
            <div style="padding:8px 12px;background:{card_bg};border:1px solid {card_bdr};
                 border-left:3px solid {col_s};border-radius:0 8px 8px 0;
                 margin-bottom:6px;font-size:13px;color:{txt};">{pt}</div>""", unsafe_allow_html=True)

    if summary.get("formulas"):
        st.markdown(f"<div style='font-size:13px;font-weight:700;color:{txt};margin:14px 0 8px;'>🔢 Formulas / Definitions</div>", unsafe_allow_html=True)
        for fm in summary["formulas"][:6]:
            st.markdown(f"""
            <div style="padding:6px 12px;background:{'#080d1a' if D else '#f0f4f8'};border:1px solid {card_bdr};
                 border-radius:8px;margin-bottom:5px;font-size:12px;color:{txt};
                 font-family:'JetBrains Mono',monospace;">{fm}</div>""", unsafe_allow_html=True)

    if summary.get("exam_tip"):
        st.markdown(f"""
        <div style="background:{'#1c1205' if D else '#fff8ee'};border:1px solid #92400e;
             border-left:3px solid #f59e0b;border-radius:0 10px 10px 0;
             padding:12px 14px;margin-top:12px;">
            <div style="font-size:11px;font-weight:700;color:#fcd34d;margin-bottom:4px;">💡 EXAM TIP</div>
            <div style="font-size:12px;color:{'#fde68a' if D else '#7c4a03'};line-height:1.6;">{summary["exam_tip"]}</div>
        </div>""", unsafe_allow_html=True)


def render_ai_study_assistant():
    t = get_theme()
    D = t["dark"]
    txt  = t["text"]
    txt2 = t["text2"]
    txt3 = t["text3"]
    bg2  = t["bg2"]
    bg3  = t["bg3"] if "bg3" in t else t["bg2"]
    bdr  = t["border"]
    bdr2 = t["border2"]
    card = t["card"] if "card" in t else t["bg2"]

    # Theme-appropriate static colors
    card_dark  = "#0d1117" if D else "#ffffff"
    card_mid   = "#0d1426" if D else "#f8fafc"
    card_line  = "#1a2540" if D else "#e2e8f0"
    txt_strong = "#f1f5f9" if D else "#0f172a"
    txt_muted  = "#475569" if D else "#64748b"
    txt_soft   = "#94a3b8" if D else "#475569"
    user_bubble_bg  = "#312e81" if D else "#ede9fe"
    user_bubble_bdr = "#4f46e5" if D else "#a5b4fc"
    user_bubble_txt = "#e2e8f0" if D else "#1e1b4b"
    ai_bubble_bg    = card_mid
    ai_bubble_bdr   = card_line
    ai_bubble_txt   = "#cbd5e1" if D else "#1e293b"
    prog_track_bg   = card_mid
    prog_track_bdr  = card_line

    st.markdown(f"""
    <div style="margin-bottom:24px;">
        <div style="font-size:24px;font-weight:800;color:{txt};">📄 AI File Analyzer & Quiz</div>
        <div style="font-size:13px;color:{txt2};margin-top:4px;">Upload notes → deep AI analysis → instant quiz → chat with your document</div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📤  Upload & Analyze", "💬  Chat with Document", "🎯  Take Quiz", "📊  History"])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — Upload & Analyze
    # ══════════════════════════════════════════════════════════
    with tabs[0]:
        col_up, col_info = st.columns([3, 2])
        with col_up:
            with st.container(border=True):
                _section("📤 Upload Study Notes", "PDF, DOCX, PPTX, TXT, PNG, JPG")
                uploaded = st.file_uploader(
                    "Drop your file here",
                    type=["pdf","docx","pptx","txt","png","jpg","jpeg"],
                    key="file_upload")
                subj_sel = st.selectbox("Subject (improves analysis)", SUBJECTS, key="up_subj")
                up_nq    = st.number_input("Number of quiz questions to generate", min_value=1, max_value=500, value=10, step=1, key="up_nq",
                                           help="How many MCQs to generate after analysis (1–500)")

                if uploaded:
                    st.markdown(f"""
                    <div style="background:{card_mid};border:1px solid {card_line};border-radius:8px;padding:12px;margin:8px 0;">
                        <div style="font-size:12px;color:{txt_muted};">Selected file</div>
                        <div style="font-size:14px;font-weight:600;color:{txt_strong};">📎 {uploaded.name}</div>
                        <div style="font-size:11px;color:{txt_muted};margin-top:2px;">{uploaded.size//1024} KB · {uploaded.type}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("⚡ Analyze File", type="primary", use_container_width=True):
                        with st.spinner("Extracting text and building deep analysis…"):
                            text    = file_reader.extract_text(uploaded)
                            wc      = file_reader.get_word_count(text)
                            summary = ai_quiz_engine.generate_summary(text)
                            mcqs    = ai_quiz_engine.generate_mcqs(text, num_questions=int(up_nq))
                            db.execute_query(
                                "INSERT INTO uploaded_study_files (filename,subject,upload_date,extracted_text) VALUES (?,?,?,?)",
                                (uploaded.name, subj_sel, datetime.now().strftime("%Y-%m-%d"), text[:2000]))
                            st.session_state.update({
                                "file_text":      text,
                                "file_summary":   summary,
                                "file_mcqs":      mcqs,
                                "file_name":      uploaded.name,
                                "file_subject":   subj_sel,
                                "file_wc":        wc,
                                "quiz_submitted": False,
                                "quiz_answers":   {},
                                "chat_history":   [],
                            })
                        st.success(f"✅ Extracted {wc:,} words. Deep analysis complete!")

        with col_info:
            num_bub = "#4f46e522" if D else "#ede9fe"
            num_txt = "#818cf8" if D else "#4f46e5"
            fmt_bdr = "#1a2540" if D else "#e2e8f0"
            fmt_bg  = "#1a2540" if D else "#f1f5f9"
            fmt_txt = "#94a3b8" if D else "#475569"
            st.markdown(f"""
            <div style="background:{card_mid};border:1px solid {card_line};
                 border-radius:14px;padding:20px;">
                <div style="font-size:13px;font-weight:700;color:{txt_strong};margin-bottom:14px;">✨ What you get</div>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <div style="display:flex;gap:10px;align-items:flex-start;">
                        <div style="background:{num_bub};border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;font-weight:800;color:{num_txt};">1</div>
                        <div style="font-size:12px;color:{txt_soft};"><b style="color:{txt_strong};">Deep Summary</b> — sections, concepts, and key sentences extracted from your file</div>
                    </div>
                    <div style="display:flex;gap:10px;align-items:flex-start;">
                        <div style="background:{num_bub};border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;font-weight:800;color:{num_txt};">2</div>
                        <div style="font-size:12px;color:{txt_soft};"><b style="color:{txt_strong};">Chat with Document</b> — ask any question and get answers from your file</div>
                    </div>
                    <div style="display:flex;gap:10px;align-items:flex-start;">
                        <div style="background:{num_bub};border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;font-weight:800;color:{num_txt};">3</div>
                        <div style="font-size:12px;color:{txt_soft};"><b style="color:{txt_strong};">Auto Quiz</b> — subject-matched MCQs with instant feedback</div>
                    </div>
                    <div style="display:flex;gap:10px;align-items:flex-start;">
                        <div style="background:{num_bub};border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;font-weight:800;color:{num_txt};">4</div>
                        <div style="font-size:12px;color:{txt_soft};"><b style="color:{txt_strong};">Exam Focus</b> — high-frequency topics and exam tips for your subject</div>
                    </div>
                </div>
                <div style="margin-top:14px;padding-top:12px;border-top:1px solid {fmt_bdr};">
                    <div style="font-size:11px;color:{txt_muted};margin-bottom:6px;">Supported formats</div>
                    <div style="display:flex;flex-wrap:wrap;gap:4px;">
                        {"".join(f'<span style="background:{fmt_bg};color:{fmt_txt};padding:2px 8px;border-radius:6px;font-size:11px;">{e}</span>' for e in ["PDF","DOCX","PPTX","TXT","PNG","JPG"])}
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        if "file_summary" in st.session_state and st.session_state["file_summary"]:
            st.divider()
            _render_rich_summary(st.session_state["file_summary"], st.session_state.get("file_name","Document"))
        elif "file_text" in st.session_state and not st.session_state.get("file_summary"):
            st.error("Could not extract sufficient text. Try a different format.")

    # ══════════════════════════════════════════════════════════
    # TAB 2 — Chat with Document
    # ══════════════════════════════════════════════════════════
    with tabs[1]:
        if "file_text" not in st.session_state or not st.session_state["file_text"]:
            st.markdown(f"""
            <div style="text-align:center;padding:60px 0;">
                <div style="font-size:48px;margin-bottom:14px;">💬</div>
                <div style="font-size:17px;font-weight:700;color:{txt};margin-bottom:6px;">No Document Loaded</div>
                <div style="font-size:13px;color:{txt2};">Upload a file in the Upload tab first,<br>then come back here to chat with it.</div>
            </div>""", unsafe_allow_html=True)
        else:
            doc_text = st.session_state["file_text"]
            topic    = st.session_state["file_summary"]["topic"] if st.session_state.get("file_summary") else "general"
            subj     = st.session_state.get("file_subject","General")
            col_s    = SC.get(subj,"#6366f1")
            fname    = st.session_state.get("file_name","Document")

            st.markdown(f"""
            <div style="background:{card_mid};border:1px solid {col_s}44;
                 border-radius:14px;padding:14px 20px;margin-bottom:16px;
                 display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:11px;color:{txt_muted};text-transform:uppercase;letter-spacing:1.5px;">Chatting with</div>
                    <div style="font-size:15px;font-weight:700;color:{txt_strong};">📎 {fname}</div>
                </div>
                <div style="display:flex;gap:8px;align-items:center;">
                    {_badge(subj, col_s)}
                    <span style="background:#05391622;color:#4ade80;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;">🟢 Ready</span>
                </div>
            </div>""", unsafe_allow_html=True)

            sugg_q = {
                "fr":    ["What is the 5-step revenue recognition model?","Explain the control concept for consolidation","Key learning outcomes?","Main concepts covered?"],
                "audit": ["Key risk assessment procedures?","Going concern evaluation process?","Learning outcomes?","What does this cover about audit evidence?"],
                "dt":    ["Capital gains tax rates?","Explain transfer pricing methods","Key learning outcomes?","Main concepts in this document?"],
                "idt":   ["Input tax credit restrictions?","Place of supply rules?","Key learning outcomes?","What does this cover about GST?"],
                "afm":   ["Explain CAPM and its application","What is EVA and how is it calculated?","Learning outcomes?","Main financial concepts?"],
                "ibs":   ["Explain Porter's Five Forces","What is the Balanced Scorecard?","Learning outcomes?","What does this say about strategy?"],
                "general":["Main topics covered?","Key learning outcomes?","Summarise the important concepts","What sections does this document have?"],
            }
            suggestions = sugg_q.get(topic, sugg_q["general"])

            st.markdown(f'<div style="font-size:12px;color:{txt_muted};margin-bottom:8px;">💡 Try asking:</div>', unsafe_allow_html=True)
            s_cols = st.columns(2)
            for si, sq in enumerate(suggestions[:4]):
                with s_cols[si % 2]:
                    if st.button(f"❝ {sq[:55]}{'…' if len(sq)>55 else ''}", key=f"sugg_{si}", use_container_width=True):
                        if "chat_history" not in st.session_state:
                            st.session_state["chat_history"] = []
                        with st.spinner("Searching document…"):
                            ans = ai_quiz_engine.answer_from_document(sq, doc_text, topic)
                        st.session_state["chat_history"].append({"role":"user","content":sq})
                        st.session_state["chat_history"].append({"role":"assistant","content":ans})
                        st.rerun()

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []
            chat_history = st.session_state["chat_history"]

            if chat_history:
                st.markdown(f'<div style="font-size:12px;color:{txt_muted};margin-bottom:10px;">Conversation</div>', unsafe_allow_html=True)
                for msg in chat_history:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style="display:flex;justify-content:flex-end;margin-bottom:10px;">
                            <div style="background:{user_bubble_bg};border:1px solid {user_bubble_bdr};
                                 border-radius:14px 14px 4px 14px;padding:12px 16px;max-width:75%;">
                                <div style="font-size:13px;color:{user_bubble_txt};line-height:1.5;">{msg['content']}</div>
                                <div style="font-size:10px;color:{col_s};margin-top:4px;text-align:right;">You</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        content_html = msg["content"].replace("\n","<br>")
                        content_html = re.sub(r'\*\*(.+?)\*\*', rf'<b style="color:{txt_strong};">\1</b>', content_html)
                        content_html = re.sub(r'\*(.+?)\*',   rf'<i style="color:{txt_soft};">\1</i>',    content_html)
                        st.markdown(f"""
                        <div style="display:flex;justify-content:flex-start;margin-bottom:10px;">
                            <div style="background:{ai_bubble_bg};border:1px solid {ai_bubble_bdr};
                                 border-radius:14px 14px 14px 4px;padding:14px 16px;max-width:85%;">
                                <div style="font-size:10px;color:{col_s};font-weight:700;margin-bottom:6px;">🤖 AI ASSISTANT</div>
                                <div style="font-size:13px;color:{ai_bubble_txt};line-height:1.7;">{content_html}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:{card_mid};border:1px dashed {card_line};border-radius:12px;
                     padding:24px;text-align:center;margin:8px 0 14px;">
                    <div style="font-size:24px;margin-bottom:8px;">💬</div>
                    <div style="font-size:13px;color:{txt2};">Ask any question about your uploaded document.<br>
                    Click a suggestion above or type your own question below.</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                user_q = st.text_input("Ask a question…", key="chat_input",
                    placeholder="e.g. What are the key learning outcomes? What does section 2 cover?",
                    )
                col_ask, col_clear = st.columns([4,1])
                with col_ask:
                    ask_clicked = st.button("🔍 Ask", type="primary", use_container_width=True)
                with col_clear:
                    if st.button("🗑 Clear", use_container_width=True):
                        st.session_state["chat_history"] = []
                        st.rerun()

            if ask_clicked and user_q.strip():
                with st.spinner("Searching your document…"):
                    answer = ai_quiz_engine.answer_from_document(user_q.strip(), doc_text, topic)
                st.session_state["chat_history"].append({"role":"user","content":user_q.strip()})
                st.session_state["chat_history"].append({"role":"assistant","content":answer})
                st.rerun()

    # ══════════════════════════════════════════════════════════
    # TAB 3 — Quiz
    # ══════════════════════════════════════════════════════════
    with tabs[2]:
        if "file_mcqs" not in st.session_state:
            st.markdown(f"""
            <div style="text-align:center;padding:40px 0 20px;">
                <div style="font-size:40px;margin-bottom:12px;">🎯</div>
                <div style="font-size:16px;font-weight:600;color:{txt};margin-bottom:6px;">No Quiz Loaded Yet</div>
                <div style="font-size:13px;color:{txt2};">Upload a file to auto-generate a quiz, or use Quick Quiz below.</div>
            </div>""", unsafe_allow_html=True)
            st.divider()
            _section("⚡ Quick Quiz", "Test yourself on any subject without uploading a file")
            qc1, qc2 = st.columns(2)
            qq_sub = qc1.selectbox("Choose Subject", ["FR","Audit","DT","IDT","AFM","IBS","General"], key="qq_sub")
            qq_n   = qc2.number_input("Number of Questions", min_value=1, max_value=500, value=5, step=1, key="qq_n")
            pool_key = qq_sub.lower() if qq_sub != "General" else "general"
            pool_sz  = ai_quiz_engine.get_pool_size(pool_key)
            st.markdown(f'<div style="font-size:11px;color:{txt2};margin-bottom:10px;">📚 {pool_sz} unique questions in {qq_sub} bank · enter any number (repeats with shuffling beyond {pool_sz})</div>', unsafe_allow_html=True)
            if st.button("🎲 Generate Quiz", type="primary"):
                import random
                pool     = ai_quiz_engine._MCQ_BANK.get(pool_key, ai_quiz_engine._MCQ_BANK["general"])
                extended = []
                while len(extended) < int(qq_n):
                    chunk = pool[:]
                    random.shuffle(chunk)
                    extended.extend(chunk)
                st.session_state.update({
                    "file_mcqs":      extended[:int(qq_n)],
                    "file_subject":   qq_sub,
                    "file_name":      f"Quick Quiz — {qq_sub}",
                    "quiz_submitted": False,
                    "quiz_answers":   {},
                })
                st.rerun()
        else:
            mcqs         = st.session_state["file_mcqs"]
            subj         = st.session_state.get("file_subject","General")
            col_s        = SC.get(subj, "#6366f1")
            already_done = st.session_state.get("quiz_submitted", False)

            if st.session_state.pop("fire_balloons", False):
                st.balloons()

            st.markdown(f"""
            <div style="background:{card_mid};border:1px solid {col_s}44;
                 border-radius:14px;padding:16px 22px;margin-bottom:20px;
                 display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:11px;color:{txt_muted};text-transform:uppercase;letter-spacing:1.5px;">Active Quiz</div>
                    <div style="font-size:15px;font-weight:700;color:{txt_strong};">{st.session_state.get("file_name","Quiz")}</div>
                </div>
                <div style="text-align:right;">
                    {_badge(subj, col_s)}
                    <div style="font-size:11px;color:{txt_muted};margin-top:4px;">{len(mcqs)} questions</div>
                </div>
            </div>""", unsafe_allow_html=True)

            if not already_done:
                if "quiz_answers" not in st.session_state:
                    st.session_state["quiz_answers"] = {}
                prev_answers = dict(st.session_state["quiz_answers"])

                for i, q in enumerate(mcqs):
                    prev      = prev_answers.get(i)
                    is_ans    = prev is not None
                    was_right = is_ans and prev == q["answer"]
                    card_bg_q  = ("#052e16" if D else "#f0fdf4") if was_right else (("#1f0505" if D else "#fef2f2") if is_ans else card_mid)
                    card_bdr_q = ("#166534" if was_right else ("#991b1b" if is_ans else card_line))

                    st.markdown(f"""
                    <div style="background:{card_bg_q};border:1px solid {card_bdr_q};border-radius:12px;
                         padding:16px 20px;margin-bottom:4px;">
                        <div style="font-size:14px;font-weight:600;color:{txt_strong};margin-bottom:4px;">
                            Q{i+1}. {q['question']}
                        </div>
                        {'<div style="font-size:12px;color:#22c55e;margin-top:4px;">✅ Correct! <b>' + str(q.get("answer","")) + '</b></div>' if was_right else ""}
                        {'<div style="font-size:12px;color:#ef4444;margin-top:4px;">❌ Wrong — Answer: <b>' + str(q.get("answer","")) + '</b></div>' if is_ans and not was_right else ""}
                    </div>""", unsafe_allow_html=True)

                    if not was_right:
                        chosen = st.radio(f"Select answer for Q{i+1}", q["options"],
                                          key=f"q_{i}", index=None)
                        if chosen is not None and chosen != prev:
                            st.session_state["quiz_answers"][i] = chosen
                            if chosen == q["answer"]:
                                st.session_state["fire_balloons"] = True
                            st.rerun()
                    else:
                        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

                answered       = sum(1 for i in range(len(mcqs)) if st.session_state["quiz_answers"].get(i) is not None)
                correct_so_far = sum(1 for i,q in enumerate(mcqs) if st.session_state["quiz_answers"].get(i)==q["answer"])
                prog_pct = round(answered/len(mcqs)*100) if mcqs else 0
                st.markdown(f"""
                <div style="background:{prog_track_bg};border:1px solid {prog_track_bdr};border-radius:10px;padding:12px 16px;margin:12px 0;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                        <span style="font-size:12px;color:{txt_muted};">Progress</span>
                        <span style="font-size:12px;font-weight:700;color:#818cf8;">{answered}/{len(mcqs)} answered · {correct_so_far} correct</span>
                    </div>
                    <div style="height:5px;background:{card_line};border-radius:4px;overflow:hidden;">
                        <div style="height:100%;width:{prog_pct}%;background:linear-gradient(90deg,#4f46e5,#818cf8);border-radius:4px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

                if answered == len(mcqs):
                    if st.button("📊 See Final Results", type="primary", use_container_width=True):
                        fa  = st.session_state["quiz_answers"]
                        cor = sum(1 for i,q in enumerate(mcqs) if fa.get(i)==q["answer"])
                        acc = round(cor/len(mcqs)*100)
                        st.session_state.update({"quiz_submitted":True,"quiz_correct":cor,"quiz_accuracy":acc})
                        db.execute_query(
                            "INSERT INTO quiz_attempts (subject,topic,total_questions,correct_answers,accuracy,attempt_date) VALUES (?,?,?,?,?,?)",
                            (subj, st.session_state.get("file_name","Quiz"), len(mcqs), cor, acc, datetime.now().strftime("%Y-%m-%d")))
                        st.rerun()
                else:
                    rem = len(mcqs) - answered
                    st.info(f"Answer {rem} more question{'s' if rem>1 else ''} to complete the quiz.")
            else:
                cor   = st.session_state.get("quiz_correct",0)
                acc   = st.session_state.get("quiz_accuracy",0)
                fa    = st.session_state.get("quiz_answers",{})
                col_r = "#22c55e" if acc>=75 else "#f59e0b" if acc>=50 else "#ef4444"
                grade = "Excellent! 🏆" if acc>=75 else "Good effort! 💪" if acc>=50 else "Needs revision 📚"
                res_card_bg = "#0d1117" if D else "#ffffff"

                st.markdown(f"""
                <div style="background:{res_card_bg};border:2px solid {col_r}44;
                     border-radius:16px;padding:28px;text-align:center;margin-bottom:24px;">
                    <div style="font-size:52px;font-weight:800;color:{col_r};font-family:'JetBrains Mono',monospace;">{acc}%</div>
                    <div style="font-size:18px;font-weight:700;color:{txt};margin:8px 0;">{grade}</div>
                    <div style="font-size:14px;color:{txt2};">{cor} of {len(mcqs)} questions correct</div>
                    <div style="height:6px;background:{card_line};border-radius:4px;overflow:hidden;margin:16px auto;max-width:300px;">
                        <div style="height:100%;width:{acc}%;background:{col_r};border-radius:4px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

                if acc == 100: st.balloons()
                elif acc >= 75: st.success("🎉 Outstanding performance!")

                _section("📋 Answer Review")
                for i,q in enumerate(mcqs):
                    ua = fa.get(i); ok = ua==q["answer"]
                    rev_bg  = ("#052e16" if D else "#f0fdf4") if ok else ("#1f0505" if D else "#fef2f2")
                    rev_bdr = "#166534" if ok else "#991b1b"
                    rev_cor = "#22c55e" if ok else "#ef4444"
                    st.markdown(f"""
                    <div style="background:{rev_bg};border:1px solid {rev_bdr};
                         border-radius:10px;padding:14px 16px;margin-bottom:8px;">
                        <div style="font-size:13px;font-weight:600;color:{txt_strong};margin-bottom:8px;">{'✅' if ok else '❌'} Q{i+1}. {q['question']}</div>
                        <div style="font-size:12px;color:#22c55e;">✔ Correct: {q['answer']}</div>
                        {f'<div style="font-size:12px;color:#ef4444;">✘ Your answer: {ua}</div>' if not ok and ua else ""}
                    </div>""", unsafe_allow_html=True)

                col_ret, col_new = st.columns(2)
                if col_ret.button("🔄 Retry", use_container_width=True):
                    st.session_state.update({"quiz_submitted":False,"quiz_answers":{}})
                    st.rerun()
                if col_new.button("🎲 New Quiz", type="primary", use_container_width=True):
                    for k in ["file_mcqs","file_summary","file_text","file_name","quiz_submitted","quiz_answers"]:
                        st.session_state.pop(k, None)
                    st.rerun()

    # ══════════════════════════════════════════════════════════
    # TAB 4 — History
    # ══════════════════════════════════════════════════════════
    with tabs[3]:
        df = db.fetch_data("SELECT attempt_date,subject,topic,total_questions,correct_answers,accuracy FROM quiz_attempts ORDER BY id DESC")
        if df.empty:
            st.info("No quiz attempts yet.")
        else:
            c1,c2,c3 = st.columns(3)
            c1.metric("Total Attempts", len(df))
            c2.metric("Avg Accuracy",   f"{df['accuracy'].mean():.1f}%")
            c3.metric("Best Score",     f"{df['accuracy'].max():.0f}%")

            df_files = db.fetch_data("SELECT filename,subject,upload_date FROM uploaded_study_files ORDER BY id DESC LIMIT 10")
            if not df_files.empty:
                st.divider()
                _section("📁 Recently Analyzed Files")
                for _,row in df_files.iterrows():
                    col_s = SC.get(str(row["subject"]),"#6366f1")
                    st.markdown(f"""
                    <div style="padding:10px 14px;background:{card_mid};border:1px solid {card_line};
                         border-radius:8px;margin-bottom:6px;
                         display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            {_badge(str(row["subject"]), col_s)}
                            <span style="color:{txt_strong};font-size:13px;margin-left:8px;">📎 {row["filename"]}</span>
                        </div>
                        <span style="color:{txt_muted};font-size:11px;">{row["upload_date"]}</span>
                    </div>""", unsafe_allow_html=True)

            st.divider()
            _section("🎯 Quiz History")
            for _,row in df.iterrows():
                acc_r = float(row["accuracy"])
                col_a = "#22c55e" if acc_r>=75 else "#f59e0b" if acc_r>=50 else "#ef4444"
                cs    = SC.get(str(row["subject"]),"#6366f1")
                st.markdown(f"""
                <div style="padding:12px 16px;background:{card_mid};border:1px solid {card_line};
                     border-radius:10px;margin-bottom:8px;
                     display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        {_badge(str(row["subject"]), cs)}
                        <span style="color:{txt_strong};font-size:13px;margin-left:8px;">{str(row["topic"])[:40]}</span>
                        <div style="color:{txt_muted};font-size:11px;margin-top:2px;">{row["attempt_date"]} · {int(row["total_questions"])} questions</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:18px;font-weight:800;color:{col_a};font-family:'JetBrains Mono',monospace;">{acc_r:.0f}%</span>
                        <div style="font-size:11px;color:{txt_muted};">{int(row["correct_answers"])}/{int(row["total_questions"])}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
