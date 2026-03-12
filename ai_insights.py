import streamlit as st
import ai_engine as engine
from datetime import datetime
import re
import urllib.parse

def _t():
    """Return theme tokens."""
    dark = st.session_state.get("theme","dark") == "dark"
    return {
        "dark": dark,
        "bg":     "#0a0a0f" if dark else "#f5f5f7",
        "bg2":    "#111118" if dark else "#ffffff",
        "bg3":    "#1a1a24" if dark else "#f2f2f4",
        "border": "#2a2a3a" if dark else "#d1d1d6",
        "text":   "#f5f5f7" if dark else "#1d1d1f",
        "text2":  "#a1a1aa" if dark else "#6e6e73",
        "text3":  "#52525b" if dark else "#aeaeb2",
        "accent": "#6366f1",
        "card":   "#111118" if dark else "#ffffff",
        "input":  "#1a1a24" if dark else "#f5f5f7",
    }

def _render_md(text):
    if not text: return ""
    t = _t()
    lines = text.split("\n")
    out = []
    in_table = False
    for line in lines:
        if line.strip().startswith("|"):
            if not in_table:
                out.append(f'<table style="width:100%;border-collapse:collapse;margin:8px 0;font-size:12px;">')
                in_table = True
            if re.match(r'^\|[-| :]+\|$', line.strip()):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            row = "".join(f'<td style="padding:5px 10px;border:1px solid {t["border"]};color:{t["text2"]};">{c}</td>' for c in cells)
            out.append(f"<tr>{row}</tr>")
        else:
            if in_table:
                out.append("</table>")
                in_table = False
            out.append(line)
    if in_table:
        out.append("</table>")
    text = "\n".join(out)
    text = re.sub(r'^### (.+)$', rf'<div style="font-size:14px;font-weight:700;color:{t["accent"]};margin:12px 0 5px;">\1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  rf'<div style="font-size:15px;font-weight:700;color:{t["accent"]};margin:14px 0 6px;">\1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', rf'<b style="color:{t["text"]}">\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     rf'<i style="color:{t["text2"]}">\1</i>', text)
    text = re.sub(r'^- (.+)$', rf'<div style="display:flex;gap:8px;margin:3px 0;"><span style="color:{t["accent"]};flex-shrink:0;">›</span><span style="color:{t["text2"]}">\1</span></div>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\. (.+)$', rf'<div style="display:flex;gap:8px;margin:3px 0;"><span style="color:{t["accent"]};font-weight:700;flex-shrink:0;">\1.</span><span style="color:{t["text2"]}">\2</span></div>', text, flags=re.MULTILINE)
    text = text.replace("---", f'<hr style="border:none;border-top:1px solid {t["border"]};margin:10px 0;">')
    text = text.replace("\n", "<br>")
    text = re.sub(r'(</div>|</table>)<br>', r'\1', text)
    return text


def render_ai_insights():
    t = _t()

    st.markdown(f"""
    <div style="margin-bottom:24px;">
        <div style="font-size:26px;font-weight:800;color:{t['text']};letter-spacing:-0.04em;">🧠 AI Study Insights</div>
        <div style="font-size:13px;color:{t['text2']};margin-top:4px;font-weight:400;">
            Smart strategy · Burnout detection · Multi-AI doubt resolution
        </div>
    </div>""", unsafe_allow_html=True)

    # Init session state
    if "doubt_history" not in st.session_state:
        st.session_state["doubt_history"] = []
    if "doubt_prefill" not in st.session_state:
        st.session_state["doubt_prefill"] = ""

    # ── Burnout card
    burnout = engine.check_burnout_risk()
    if burnout["risk"] == "High":
        st.markdown(f"""
        <div style="background:{"#1f0505" if t['dark'] else "#fef2f2"};
             border:1px solid {"#7f1d1d" if t['dark'] else "#fecaca"};
             border-radius:14px;padding:14px 20px;margin-bottom:18px;display:flex;gap:12px;align-items:flex-start;">
            <span style="font-size:18px;">🚨</span>
            <div>
                <div style="font-size:13px;font-weight:700;color:{"#fca5a5" if t['dark'] else "#991b1b"};">
                    Burnout Risk Detected
                </div>
                <div style="font-size:12px;color:{"#f87171" if t['dark'] else "#b91c1c"};margin-top:2px;">
                    {burnout["message"]} — {burnout["plan"]}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:{"#052e16" if t['dark'] else "#f0fdf4"};
             border:1px solid {"#14532d" if t['dark'] else "#bbf7d0"};
             border-radius:14px;padding:12px 20px;margin-bottom:18px;display:flex;gap:10px;align-items:center;">
            <span>✅</span>
            <div style="font-size:13px;color:{"#86efac" if t['dark'] else "#166534"};font-weight:500;">
                Pacing healthy — {burnout["message"]}
            </div>
        </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    # ── Strategy card
    with col_l:
        with st.container(border=True):
            st.markdown(f'<div style="font-size:15px;font-weight:700;color:{t["text"]};margin-bottom:10px;letter-spacing:-0.02em;">🎯 Tomorrow\'s Study Strategy</div>', unsafe_allow_html=True)
            exam_str = st.session_state.get("exam_date", "2026-05-01")
            try:
                days_left = max(0, (datetime.strptime(exam_str, "%Y-%m-%d") - datetime.now()).days)
            except:
                days_left = 0
            strategy = engine.generate_daily_strategy(days_left)
            st.markdown(f"""
            <div style="background:{t['bg']};border-radius:10px;padding:14px 16px;
                 font-size:13px;color:{t['text2']};line-height:1.85;border:1px solid {t['border']};">
                {_render_md(strategy)}
            </div>""", unsafe_allow_html=True)

    # ── AI Doubt Assistant
    with col_r:
        with st.container(border=True):
            st.markdown(f"""
            <div style="font-size:15px;font-weight:700;color:{t['text']};
                 letter-spacing:-0.02em;margin-bottom:2px;">🤖 AI Doubt Assistant</div>
            <div style="font-size:12px;color:{t['text2']};margin-bottom:14px;">
                Type your doubt → click an AI to get an instant answer in their app
            </div>""", unsafe_allow_html=True)

            # ── Recent questions as quick-fill chips (dynamic)
            recent_qs = [m["content"] for m in st.session_state["doubt_history"] if m["role"] == "user"]
            recent_qs = list(dict.fromkeys(recent_qs))[-6:]  # last 6 unique, no duplicates

            if recent_qs:
                st.markdown(f'<div style="font-size:10px;color:{t["text3"]};text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:6px;">Recent Questions</div>', unsafe_allow_html=True)
                chip_cols = st.columns(2)
                for i, q in enumerate(reversed(recent_qs)):
                    label = q[:28] + "…" if len(q) > 28 else q
                    with chip_cols[i % 2]:
                        if st.button(label, key=f"recent_{i}", use_container_width=True):
                            st.session_state["doubt_prefill"] = q
                            st.rerun()

            # ── Preset topics (only shown when no history)
            else:
                preset_topics = [
                    ("CAPM & Beta", "Explain CAPM formula, Beta calculation and how to use it in AFM problems"),
                    ("Derivatives", "Explain Futures and Options in AFM with hedging examples and formulas"),
                    ("Ind AS 115",  "Explain Ind AS 115 Revenue Recognition 5-step model with examples"),
                    ("GST ITC",     "Explain GST Input Tax Credit conditions and blocked credits Section 17(5)"),
                    ("Capital Gains","Explain Capital Gains — STCG LTCG tax rates and Section 54 exemptions"),
                    ("SA 315 Risk", "Explain SA 315 Risk Assessment in Audit with examples"),
                    ("Transfer Pricing","Explain Transfer Pricing methods and Form 3CEB documentation"),
                    ("Porter's Forces","Explain Porter's Five Forces framework for IBS CA Final"),
                ]
                st.markdown(f'<div style="font-size:10px;color:{t["text3"]};text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:6px;">Suggested Topics</div>', unsafe_allow_html=True)
                chip_cols = st.columns(2)
                for i, (label, full_q) in enumerate(preset_topics):
                    with chip_cols[i % 2]:
                        if st.button(label, key=f"preset_{i}", use_container_width=True):
                            st.session_state["doubt_prefill"] = full_q
                            st.rerun()

            # ── Text input
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            prefill_val = st.session_state.pop("doubt_prefill", "") if "doubt_prefill" in st.session_state else ""
            query = st.text_area(
                "Your question",
                value=prefill_val,
                height=100,
                key="doubt_query_main",
                placeholder="e.g. Explain CAPM formula and Beta with a solved numerical example for CA Final AFM...",
                label_visibility="collapsed"
            )

            # ── Save to history on ask
            if query.strip() and query.strip() not in [m["content"] for m in st.session_state["doubt_history"] if m["role"] == "user"]:
                pass  # will add when button clicked

            # ── AI Buttons ─────────────────────────────────────────
            q_text = query.strip()

            # Save question to history automatically when non-empty
            if q_text:
                hist = st.session_state.get("doubt_history", [])
                already = any(m.get("content") == q_text and m.get("role") == "user" for m in hist[-3:])
                if not already:
                    st.session_state["doubt_history"].append({"role":"user","content":q_text})

            # ── AI Buttons with correct autofill URLs ──────────────
            # ChatGPT: use /chat endpoint with direct message injection via JS
            # Claude: q= param works natively
            # Gemini: prompt= param
            default_q   = "Help me with CA Final exam preparation"
            q_safe      = q_text if q_text else default_q
            encoded     = urllib.parse.quote(q_safe)
            # Claude: ?q= pre-fills the prompt input on claude.ai
            claude_url  = f"https://claude.ai/new?q={encoded}"
            # ChatGPT: ?q= pre-fills on chatgpt.com
            chatgpt_url = f"https://chatgpt.com/?q={encoded}"
            # Gemini: ?q= pre-fills the prompt on gemini.google.com
            gemini_url  = f"https://gemini.google.com/app?q={encoded}"

            copy_bg   = "rgba(255,255,255,0.08)" if t['dark'] else "rgba(0,0,0,0.06)"
            copy_col  = t['text2']
            copy_brd  = t['border']

            hint_icon = "✅" if q_text else "⚡"
            hint_msg  = "Click to open AI with your question pre-filled:" if q_text else "Type a question above, then:"

            q_repr = repr(q_text if q_text else "Help me with CA Final exam preparation")

            st.markdown(f"""
            <style>
            .doubt-wrap {{ display:flex; gap:8px; flex-wrap:wrap; margin:10px 0 6px; }}
            .dbtn {{
                display:inline-flex; align-items:center; gap:6px;
                padding:9px 18px; border-radius:24px; font-size:13px;
                font-weight:800 !important; text-decoration:none!important;
                cursor:pointer; white-space:nowrap; letter-spacing:0.01em;
                line-height:1.3; border:none; transition:filter .15s,box-shadow .15s;
            }}
            .dbtn-copy {{
                background:{copy_bg}; color:{copy_col}!important;
                border:1.5px solid {copy_brd}!important;
            }}
            .dbtn-copy:hover {{ border-color:{t['accent']}!important; color:{t['accent']}!important; }}
            .dbtn-claude {{
                background:linear-gradient(135deg,#6d28d9,#8b5cf6);
                color:#ffffff!important;
                box-shadow:0 3px 14px rgba(109,40,217,0.5);
            }}
            .dbtn-claude:hover {{ filter:brightness(1.12); box-shadow:0 5px 20px rgba(109,40,217,0.6); }}
            .dbtn-chatgpt {{
                background:linear-gradient(135deg,#059669,#047857);
                color:#ffffff!important;
                box-shadow:0 3px 14px rgba(5,150,105,0.5);
            }}
            .dbtn-chatgpt:hover {{ filter:brightness(1.12); box-shadow:0 5px 20px rgba(5,150,105,0.6); }}
            .dbtn-gemini {{
                background:linear-gradient(135deg,#1d4ed8,#2563eb);
                color:#ffffff!important;
                box-shadow:0 3px 14px rgba(29,78,216,0.5);
            }}
            .dbtn-gemini:hover {{ filter:brightness(1.12); box-shadow:0 5px 20px rgba(29,78,216,0.6); }}
            </style>

            <script>
            function openWithClipboard(text, url) {{
              // Copy to clipboard first, then open tab after clipboard write completes
              if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(function() {{
                  window.open(url, '_blank');
                }}).catch(function() {{
                  // Fallback: legacy copy then open
                  var ta = document.createElement('textarea');
                  ta.value = text; ta.style.position='fixed'; ta.style.opacity='0';
                  document.body.appendChild(ta); ta.select();
                  try {{ document.execCommand('copy'); }} catch(e) {{}}
                  document.body.removeChild(ta);
                  window.open(url, '_blank');
                }});
              }} else {{
                var ta = document.createElement('textarea');
                ta.value = text; ta.style.position='fixed'; ta.style.opacity='0';
                document.body.appendChild(ta); ta.select();
                try {{ document.execCommand('copy'); }} catch(e) {{}}
                document.body.removeChild(ta);
                window.open(url, '_blank');
              }}
            }}
            </script>

            <div style="font-size:12px;color:{t['text2']};margin-bottom:8px;font-weight:500;">
              {hint_icon} {hint_msg}
            </div>
            <div class="doubt-wrap">
              <a class="dbtn dbtn-copy" href="#"
                 onclick="navigator.clipboard.writeText({q_repr}).then(()=>{{this.textContent='✅ Copied!';setTimeout(()=>{{this.textContent='📋 Copy'}},1500)}});return false;">
                📋 Copy
              </a>
              <a class="dbtn dbtn-chatgpt" href="{chatgpt_url}" target="_blank" rel="noopener">
                ✦ Ask ChatGPT
              </a>
              <a class="dbtn dbtn-claude" href="#"
                 onclick="openWithClipboard({q_repr}, 'https://claude.ai/new'); return false;">
                ◆ Ask Claude <span style="font-size:10px;opacity:0.75;">(pastes)</span>
              </a>
              <a class="dbtn dbtn-gemini" href="#"
                 onclick="openWithClipboard({q_repr}, 'https://gemini.google.com/app'); return false;">
                ✦ Ask Gemini <span style="font-size:10px;opacity:0.75;">(pastes)</span>
              </a>
            </div>
            <div style="font-size:10px;color:{t['text3']};margin-top:6px;line-height:1.6;">
              ChatGPT auto-fills · Claude &amp; Gemini: question copied to clipboard → just press <b>Ctrl+V</b> (or ⌘V) to paste
            </div>
            """, unsafe_allow_html=True)

            # Save query to history when non-empty
            if q_text:
                hist = st.session_state.get("doubt_history", [])
                if not hist or hist[-1].get("content") != q_text or hist[-1].get("role") != "user":
                    pass  # Only save when explicitly submitted — shown below
                # Clear history button
                if hist:
                    if st.button("🗑 Clear history", key="clear_hist"):
                        st.session_state["doubt_history"] = []
                        st.rerun()

            # ── Local KB answer
            if q_text:
                kb = engine._local_kb_fallback(q_text)
                if "Topic Not Found" not in kb:
                    st.markdown(f'<div style="height:8px"></div>', unsafe_allow_html=True)
                    with st.expander("📚 Quick local answer (offline KB)"):
                        st.markdown(f'<div style="font-size:13px;color:{t["text2"]};line-height:1.8;">{_render_md(kb)}</div>', unsafe_allow_html=True)

            # Track question in history on any interaction
            if q_text:
                hist = st.session_state.get("doubt_history", [])
                user_msgs = [m["content"] for m in hist if m["role"] == "user"]
                if q_text not in user_msgs:
                    hist.append({"role": "user", "content": q_text})
                    st.session_state["doubt_history"] = hist

    # ── Study Tips
    st.divider()
    st.markdown(f'<div style="font-size:15px;font-weight:700;color:{t["text"]};letter-spacing:-0.02em;margin-bottom:14px;">💡 Smart Study Tips</div>', unsafe_allow_html=True)
    tips = [
        ("🧠", "Active Recall",    "Close the book and write what you remember. Doubles retention vs passive re-reading."),
        ("🔁", "Spaced Repetition","Science-backed scheduling. One missed revision reduces retention by 40%."),
        ("⏱️", "50-10 Split",      "50 min focus + 10 min break. Far better than marathon sessions."),
        ("📝", "Past Papers First","Check how a chapter is examined before studying it. Shapes your approach."),
        ("🎯", "One Weak Area/Day","2 hours daily on your weakest chapter until scores improve."),
        ("😴", "Sleep > Cramming", "Memory consolidates during sleep. Early bed beats late-night study."),
    ]
    cols = st.columns(3)
    for i, (icon, title, body) in enumerate(tips):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
                 padding:16px 18px;margin-bottom:12px;transition:all .15s ease;">
                <div style="font-size:20px;margin-bottom:8px;">{icon}</div>
                <div style="font-size:13px;font-weight:600;color:{t['text']};
                     margin-bottom:4px;letter-spacing:-0.01em;">{title}</div>
                <div style="font-size:12px;color:{t['text2']};line-height:1.6;">{body}</div>
            </div>""", unsafe_allow_html=True)
