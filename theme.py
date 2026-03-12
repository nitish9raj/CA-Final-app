import streamlit as st

def get_theme():
    theme_key = st.session_state.get("theme", "dark")
    cache_key  = f"_theme_cache_{theme_key}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    dark = theme_key == "dark"
    if dark:
        t = {
            "dark": True,
            "bg":    "#080c14",
            "bg2":   "#0d1117",
            "bg3":   "#0f1923",
            "card":  "#0d1117",
            "border":  "rgba(255,255,255,0.07)",
            "border2": "rgba(255,255,255,0.12)",
            "text":  "#e8eaf0",
            "text2": "#6b7280",
            "text3": "#374151",
            "accent":   "#00f5c4",
            "accent2":  "#7b68ee",
            "accent3":  "#f5a623",
            "accent4":  "#ff6b9d",
            "accent5":  "#56ccf2",
            "input":  "#0d1117",
            "shadow": "rgba(0,0,0,0.7)",
            "nhov":   "rgba(0,245,196,0.06)",
            "nact":   "rgba(0,245,196,0.10)",
            "plot_bg":   "rgba(0,0,0,0)",
            "plot_font": "#6b7280",
            "plot_grid": "rgba(255,255,255,0.06)",
            "success_bg": "#041a10", "success_bd": "#00f5c4", "success_tx": "#00f5c4",
            "info_bg":    "#06111e", "info_bd":    "#56ccf2", "info_tx":    "#56ccf2",
            "warn_bg":    "#1a1200", "warn_bd":    "#f5a623", "warn_tx":    "#f5a623",
            "err_bg":     "#1a0610", "err_bd":     "#ff6b9d", "err_tx":     "#ff6b9d",
        }
    else:
        t = {
            "dark": False,
            "bg":    "#f0f4f8",
            "bg2":   "#ffffff",
            "bg3":   "#e8edf5",
            "card":  "#ffffff",
            "border":  "rgba(0,0,0,0.08)",
            "border2": "rgba(0,0,0,0.14)",
            "text":  "#0d1117",
            "text2": "#4b5563",
            "text3": "#9ca3af",
            "accent":   "#00b894",
            "accent2":  "#6c5ce7",
            "accent3":  "#e17055",
            "accent4":  "#e84393",
            "accent5":  "#0984e3",
            "input":  "#f0f4f8",
            "shadow": "rgba(0,0,0,0.08)",
            "nhov":   "rgba(0,184,148,0.07)",
            "nact":   "rgba(0,184,148,0.12)",
            "plot_bg":   "rgba(0,0,0,0)",
            "plot_font": "#4b5563",
            "plot_grid": "rgba(0,0,0,0.07)",
            "success_bg": "#edfdf8", "success_bd": "#00b894", "success_tx": "#00785e",
            "info_bg":    "#eaf6ff", "info_bd":    "#0984e3", "info_tx":    "#065a9e",
            "warn_bg":    "#fff8ee", "warn_bd":    "#e17055", "warn_tx":    "#9a3f1e",
            "err_bg":     "#fff0f5", "err_bd":     "#e84393", "err_tx":     "#8b0052",
        }
    st.session_state[cache_key] = t
    return t
