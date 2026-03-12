# CA Final AI Suite v7.0 — Cloud Deployment Guide
## From Local Python App → Live SaaS in ~30 Minutes

---

## What Changed from v6 (Local) → v7 (Cloud)

| Component     | v6 Local          | v7 Cloud                        |
|---------------|-------------------|---------------------------------|
| Database      | SQLite (.db file) | Supabase PostgreSQL (cloud)     |
| Auth          | None              | Firebase (Email / Google / OTP) |
| Hosting       | Your laptop       | Streamlit Community Cloud       |
| Data sync     | Single device     | Any device, anywhere            |
| User isolation| None (shared db)  | Per-user row-level security     |

---

## STEP 1 — Set Up Supabase (Database)

**Time: ~5 minutes | Cost: Free forever**

1. Go to **https://supabase.com** → Sign Up (no credit card needed)
2. Click **"New Project"** → enter a name like `ca-final-app` → choose a database password
3. Wait ~2 minutes for project to be created
4. In the left sidebar → click **"SQL Editor"**
5. Click **"New Query"** → paste the entire contents of `schema.sql` → click **"Run"**
   - This creates all 13 tables with user_id on every table
6. Go to **Settings → API**
   - Copy **"Project URL"** → this is your `SUPABASE_URL`
   - Under "Project API Keys" → copy the **"service_role"** key (the long one) → this is your `SUPABASE_KEY`
   - ⚠️ Use `service_role` NOT `anon` — the service key lets your backend bypass RLS safely

---

## STEP 2 — Set Up Firebase (Authentication)

**Time: ~10 minutes | Cost: Free forever**

### 2a. Create Firebase Project
1. Go to **https://console.firebase.google.com**
2. Click **"Add project"** → name it `ca-final-auth` → disable Google Analytics (optional)
3. Click the **"</>"** (Web app) icon → register app → name it `CA Final`
4. Copy the `firebaseConfig` values — you'll need them in secrets.toml

### 2b. Enable Authentication Methods
1. Left sidebar → **Authentication → Get Started**
2. Click **"Sign-in method"** tab:
   - **Email/Password** → Enable → Save ✅
   - **Google** → Enable → add your email as support email → Save ✅
   - **Phone** → Enable (requires Blaze plan for production; works in test mode free) ✅

### 2c. Get Google OAuth Credentials (for Google login)
1. Go to **https://console.cloud.google.com**
2. Select the same project
3. **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
4. Application type: **Web application**
5. Under "Authorized redirect URIs" add:
   - `http://localhost:8501` (for local testing)
   - `https://your-app-name.streamlit.app` (for production — fill in after Step 4)
6. Copy **Client ID** and **Client Secret**

---

## STEP 3 — Fill in secrets.toml

Open `.streamlit/secrets.toml` and replace every placeholder:

```toml
SUPABASE_URL = "https://abcxyz.supabase.co"
SUPABASE_KEY = "eyJ..."                      # service_role key

FIREBASE_API_KEY             = "AIzaSy..."
FIREBASE_AUTH_DOMAIN         = "ca-final-auth.firebaseapp.com"
FIREBASE_PROJECT_ID          = "ca-final-auth"
FIREBASE_STORAGE_BUCKET      = "ca-final-auth.appspot.com"
FIREBASE_MESSAGING_SENDER_ID = "123456789"
FIREBASE_APP_ID              = "1:123:web:abc"

GOOGLE_CLIENT_ID     = "123.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-..."
OAUTH_REDIRECT_URI   = "http://localhost:8501"   # change after deploy

ANTHROPIC_API_KEY = "sk-ant-..."
```

---

## STEP 4 — Deploy to Streamlit Cloud

**Time: ~5 minutes | Cost: Free**

1. Push your `ca_saas/` folder to a **GitHub repository**
   ```bash
   cd ca_saas
   git init
   git add .
   git commit -m "CA Final AI Suite v7.0 Cloud"
   git remote add origin https://github.com/YOUR_USERNAME/ca-final-app.git
   git push -u origin main
   ```

2. Go to **https://share.streamlit.io** → Sign in with GitHub
3. Click **"New app"** → select your repo → set:
   - **Main file path:** `main.py`
   - **Branch:** `main`
4. Click **"Advanced settings"** → paste the contents of `secrets.toml` into the Secrets box
5. Click **"Deploy!"** → wait ~2 minutes
6. Your app will be live at `https://your-app-name.streamlit.app`

7. Go back to Firebase → Authentication → Settings → Authorized domains → add your Streamlit URL
8. Go back to Google Cloud → OAuth credentials → add your Streamlit URL to authorized redirects
9. Update `OAUTH_REDIRECT_URI` in secrets to your Streamlit URL

---

## STEP 5 — Test Everything

| Test | Expected Result |
|------|----------------|
| Open app URL | Login page appears (no blank screen) |
| Register with email | Account created, redirected to dashboard |
| Sign out → sign in again | All data persisted |
| Open on phone | Same data, same account |
| Google login | Redirects to Google, returns logged in |
| Settings → Exam Date | Saves to cloud, survives browser refresh |

---

## Architecture Overview

```
Browser (Streamlit)
    │
    ├── auth.py ─────────────────→ Firebase Auth API
    │   Email / Google / OTP          (identity)
    │
    ├── database.py ─────────────→ Supabase PostgreSQL
    │   fetch_data() / execute_query()    (your data)
    │   All queries auto-filtered         table.user_id = uid
    │   by logged-in user_id
    │
    └── modules/ (unchanged)
        All 13 feature modules work
        identically — they still call
        db.fetch_data() and
        db.execute_query() as before.
```

## Database Tables (all have user_id)

```
users              — synced from Firebase, stores exam_date
study_sessions     — date, subject, category, duration_minutes
mock_tests         — date, subject, marks_obtained, total_marks
notes              — title, content, is_mistake
revisions          — chapter_id, rev1..4 dates and statuses
daily_targets      — date, target_hours, notes
syllabus           — subject, chapter, status, weightage
topic_progress     — subject, topic_name, status, confidence
lectures           — subject, lecture_name, watched_duration
practice_questions — subject, chapter, source, status
quiz_attempts      — subject, topic, accuracy
uploaded_study_files — filename, subject, extracted_text
icai_materials     — shared reference data (no user_id)
```

---

## Troubleshooting

**"SUPABASE_URL not found"**
→ Check secrets.toml is filled and uploaded to Streamlit Cloud secrets

**"Invalid API key" on Firebase**
→ Make sure you're using FIREBASE_API_KEY (the web API key, not a service account)

**Google login doesn't redirect back**
→ Add your Streamlit URL to authorized redirect URIs in Google Cloud Console

**Phone OTP says "BILLING_NOT_ENABLED"**
→ Firebase Phone Auth requires Blaze (pay-as-you-go) plan for production.
  It works in test mode for development.

**Data not showing after login**
→ Check that you ran schema.sql in Supabase SQL editor successfully
→ Check SUPABASE_KEY is the service_role key (not anon)
