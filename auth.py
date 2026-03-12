"""
auth.py — Firebase Authentication
Supports: Email/Password, Google OAuth, Phone OTP
"""
import streamlit as st
import requests
import re
import database as db
from theme import get_theme

_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"

def _key():
    return st.secrets["FIREBASE_API_KEY"]

def _post(endpoint: str, body: dict) -> dict:
    r = requests.post(f"{_BASE}:{endpoint}?key={_key()}", json=body, timeout=12)
    return r.json()

# ── Session helpers ──────────────────────────────────────────
def is_logged_in() -> bool:
    return bool(st.session_state.get("user_id"))

def get_user() -> dict:
    return {
        "uid":      st.session_state.get("user_id", ""),
        "email":    st.session_state.get("user_email", ""),
        "name":     st.session_state.get("user_name", "User"),
        "photo":    st.session_state.get("user_photo", ""),
        "provider": st.session_state.get("auth_provider", "email"),
    }

def _save_session(uid, email, name, photo="", provider="email"):
    st.session_state["user_id"]       = uid
    st.session_state["user_email"]    = email
    st.session_state["user_name"]     = name or (email.split("@")[0] if email else "User")
    st.session_state["user_photo"]    = photo
    st.session_state["auth_provider"] = provider
    db.upsert_user(uid, email, st.session_state["user_name"], photo)

def logout():
    for k in ["user_id","user_email","user_name","user_photo","auth_provider",
              "exam_date_synced","otp_session","otp_phone"]:
        st.session_state.pop(k, None)
    st.rerun()

# ── Email / Password ─────────────────────────────────────────
def sign_in_email(email: str, password: str) -> tuple[bool, str]:
    res = _post("signInWithPassword",
                {"email": email, "password": password, "returnSecureToken": True})
    if "idToken" in res:
        _save_session(res["localId"], email,
                      res.get("displayName",""), res.get("photoUrl",""), "email")
        return True, "Signed in!"
    return False, _err(res)

def sign_up_email(email: str, password: str, name: str) -> tuple[bool, str]:
    res = _post("signUp", {"email": email, "password": password, "returnSecureToken": True})
    if "idToken" in res:
        # Set display name
        _post("update", {"idToken": res["idToken"], "displayName": name, "returnSecureToken": False})
        _save_session(res["localId"], email, name, provider="email")
        return True, "Account created!"
    return False, _err(res)

def send_reset_email(email: str) -> tuple[bool, str]:
    res = _post("sendOobCode", {"requestType": "PASSWORD_RESET", "email": email})
    return ("email" in res), (f"Reset link sent to {email}" if "email" in res else _err(res))

# ── Google OAuth ─────────────────────────────────────────────
def google_oauth_url() -> str:
    client_id   = st.secrets.get("GOOGLE_CLIENT_ID", "")
    redirect    = st.secrets.get("OAUTH_REDIRECT_URI", "http://localhost:8501")
    scope       = "openid%20email%20profile"
    return (f"https://accounts.google.com/o/oauth2/auth"
            f"?client_id={client_id}&redirect_uri={redirect}"
            f"&response_type=code&scope={scope}&prompt=select_account")

def handle_google_callback(id_token: str) -> tuple[bool, str]:
    res = _post("signInWithIdp", {
        "requestUri": "http://localhost",
        "postBody": f"id_token={id_token}&providerId=google.com",
        "returnSecureToken": True,
    })
    if "idToken" in res:
        _save_session(res["localId"], res.get("email",""),
                      res.get("displayName",""), res.get("photoUrl",""), "google")
        return True, "Signed in with Google!"
    return False, _err(res)

# ── Phone OTP ────────────────────────────────────────────────
def send_otp(phone: str) -> tuple[bool, str]:
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendVerificationCode?key={_key()}"
        res = requests.post(url, json={"phoneNumber": phone, "recaptchaToken": "test"}, timeout=12).json()
        if "sessionInfo" in res:
            st.session_state["otp_session"] = res["sessionInfo"]
            st.session_state["otp_phone"]   = phone
            return True, f"OTP sent to {phone}"
        return False, _err(res)
    except Exception as e:
        return False, str(e)

def verify_otp(code: str) -> tuple[bool, str]:
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPhoneNumber?key={_key()}"
        res = requests.post(url, json={
            "sessionInfo": st.session_state.get("otp_session",""),
            "code": code
        }, timeout=12).json()
        if "idToken" in res:
            phone = st.session_state.get("otp_phone","")
            _save_session(res["localId"], phone, phone, provider="phone")
            st.session_state.pop("otp_session", None)
            return True, "Phone verified!"
        return False, _err(res)
    except Exception as e:
        return False, str(e)

# ── Error messages ───────────────────────────────────────────
def _err(res: dict) -> str:
    code = res.get("error", {}).get("message", "Unknown error")
    MAP  = {
        "EMAIL_EXISTS":              "Email already registered. Try signing in.",
        "INVALID_EMAIL":             "Invalid email address.",
        "WEAK_PASSWORD":             "Password needs at least 6 characters.",
        "EMAIL_NOT_FOUND":           "No account with that email.",
        "INVALID_PASSWORD":          "Wrong password.",
        "INVALID_LOGIN_CREDENTIALS": "Wrong email or password.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Try again later.",
        "USER_DISABLED":             "This account has been disabled.",
    }
    for k, v in MAP.items():
        if k in code:
            return v
    return code.replace("_", " ").capitalize()

# ════════════════════════════════════════════════════════════
#  LOGIN PAGE UI
# ════════════════════════════════════════════════════════════
def render_login_page():
    t = get_theme()
    D = t["dark"]
    txt   = t["text"]
    txt2  = t["text2"]
    txt3  = t["text3"]
    accent = t["accent"]
    grad   = t.get("grad", "linear-gradient(135deg,#00f5c4,#7b68ee)")
    card   = t["card"]
    border = t["border2"]
    inp    = t.get("input", t["bg2"])
    bg     = t["bg"]
    shadow = t["shadow"]

    # ── Hide sidebar, center layout ───────────────────────────
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"]{{display:none!important;}}
    .main .block-container{{max-width:460px!important;margin:0 auto!important;
      padding:40px 20px 60px!important;}}
    </style>

    <div style="text-align:center;margin-bottom:32px;padding-top:10px;">
      <div style="font-size:52px;margin-bottom:12px;line-height:1;">🎯</div>
      <div style="font-size:26px;font-weight:800;letter-spacing:-0.05em;
           background:{grad};-webkit-background-clip:text;
           -webkit-text-fill-color:transparent;background-clip:text;">
        CA Final AI Suite</div>
      <div style="font-size:13px;color:{txt2};margin-top:6px;letter-spacing:0.01em;">
        Cloud Edition · Your prep, synced everywhere</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Auth method tabs ──────────────────────────────────────
    method = st.radio("Login method", ["📧 Email", "📱 OTP", "🔗 Google"],
                      horizontal=True, label_visibility="collapsed", key="_auth_method")

    with st.container(border=True):
        if method == "📧 Email":
            _email_ui(t)
        elif method == "📱 OTP":
            _otp_ui(t)
        elif method == "🔗 Google":
            _google_ui(t)

    st.markdown(f"""
    <div style="text-align:center;margin-top:18px;font-size:11px;color:{txt3};">
      🔒 Powered by Firebase Auth · Data in PostgreSQL · Free forever
    </div>""", unsafe_allow_html=True)


def _email_ui(t):
    txt   = t["text"]
    txt2  = t["text2"]
    mode  = st.radio("Select", ["Sign In", "Create Account", "Forgot Password"],
                     horizontal=True, label_visibility="collapsed", key="_email_mode")

    if mode == "Sign In":
        st.markdown(f"<p style='color:{txt};font-weight:700;font-size:16px;margin-bottom:4px;'>Welcome back 👋</p>", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="you@example.com", key="si_email")
        pwd   = st.text_input("Password", type="password", placeholder="••••••••", key="si_pwd")
        if st.button("Sign In →", type="primary", use_container_width=True):
            if not email or not pwd:
                st.error("Enter both email and password.")
            else:
                with st.spinner("Signing in…"):
                    ok, msg = sign_in_email(email.strip(), pwd)
                if ok: st.rerun()
                else:  st.error(msg)

    elif mode == "Create Account":
        st.markdown(f"<p style='color:{txt};font-weight:700;font-size:16px;margin-bottom:4px;'>Create your account 🚀</p>", unsafe_allow_html=True)
        name  = st.text_input("Full Name", placeholder="Nitish Kumar", key="su_name")
        email = st.text_input("Email", placeholder="you@example.com", key="su_email")
        pwd   = st.text_input("Password (min 6 chars)", type="password", key="su_pwd")
        pwd2  = st.text_input("Confirm Password", type="password", key="su_pwd2")
        if st.button("Create Account →", type="primary", use_container_width=True):
            if not all([name, email, pwd, pwd2]):
                st.error("Please fill all fields.")
            elif pwd != pwd2:
                st.error("Passwords don't match.")
            elif len(pwd) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                with st.spinner("Creating account…"):
                    ok, msg = sign_up_email(email.strip(), pwd, name.strip())
                if ok: st.rerun()
                else:  st.error(msg)

    elif mode == "Forgot Password":
        st.markdown(f"<p style='color:{txt};font-weight:700;font-size:16px;margin-bottom:4px;'>Reset Password 🔑</p>", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="you@example.com", key="rp_email")
        if st.button("Send Reset Link →", type="primary", use_container_width=True):
            if not email:
                st.error("Enter your email.")
            else:
                ok, msg = send_reset_email(email.strip())
                if ok: st.success(msg)
                else:  st.error(msg)


def _otp_ui(t):
    txt = t["text"]
    st.markdown(f"<p style='color:{txt};font-weight:700;font-size:16px;margin-bottom:4px;'>Phone OTP Login 📱</p>", unsafe_allow_html=True)

    if "otp_session" not in st.session_state:
        phone = st.text_input("Phone Number", placeholder="+91 98765 43210", key="otp_phone_in")
        st.caption("Include country code, e.g. +91 for India")
        if st.button("Send OTP →", type="primary", use_container_width=True):
            if not phone.strip():
                st.error("Enter your phone number.")
            else:
                with st.spinner("Sending OTP…"):
                    ok, msg = send_otp(phone.strip())
                if ok: st.success(msg); st.rerun()
                else:  st.error(msg)
    else:
        phone = st.session_state.get("otp_phone","")
        st.info(f"OTP sent to **{phone}**")
        code = st.text_input("Enter 6-digit OTP", max_chars=6, key="otp_code_in")
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button("Verify OTP →", type="primary", use_container_width=True):
                if len(code.strip()) != 6:
                    st.error("Enter the full 6-digit OTP.")
                else:
                    with st.spinner("Verifying…"):
                        ok, msg = verify_otp(code.strip())
                    if ok: st.rerun()
                    else:  st.error(msg)
        with c2:
            if st.button("Resend", use_container_width=True):
                st.session_state.pop("otp_session", None)
                st.rerun()


def _google_ui(t):
    txt  = t["text"]
    txt2 = t["text2"]
    st.markdown(f"<p style='color:{txt};font-weight:700;font-size:16px;margin-bottom:10px;'>Sign in with Google</p>", unsafe_allow_html=True)

    gurl = google_oauth_url()
    st.markdown(f"""
    <a href="{gurl}" target="_self" style="
        display:flex;align-items:center;justify-content:center;gap:10px;
        width:100%;padding:12px 20px;border-radius:10px;
        background:#ffffff;border:1.5px solid #dadce0;
        text-decoration:none;font-size:14px;font-weight:600;
        color:#3c4043;box-shadow:0 1px 4px rgba(0,0,0,0.12);cursor:pointer;
        transition:box-shadow .15s;">
      <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
           style="width:20px;height:20px;">
      Continue with Google
    </a>""", unsafe_allow_html=True)
    st.caption("You'll be redirected to Google and back automatically.")

    # Handle callback token in URL
    params = st.query_params
    if "id_token" in params:
        with st.spinner("Completing Google sign-in…"):
            ok, msg = handle_google_callback(params["id_token"])
        if ok:
            st.query_params.clear()
            st.rerun()
        else:
            st.error(msg)
