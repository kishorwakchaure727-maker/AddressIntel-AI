# Streamlit Cloud Deployment Guide - AddressIntel AI

## Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)
- Your app files ready

## Step-by-Step Deployment

### 1. Prepare Your GitHub Repository

**Create a new GitHub repo:**
```bash
cd f:\dataveris
git init
git add .
git commit -m "Initial commit - AddressIntel AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

**Files included:**
- ✅ `app.py` - Main application
- ✅ `agent_logic.py` - AI extraction logic
- ✅ `user_db.py` - User database handler
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System dependencies (Playwright)
- ✅ `.streamlit/config.toml` - App configuration
- ✅ `README.md` - Documentation

### 2. Deploy on Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Sign in** with GitHub
3. **Click**: "New app"
4. **Configure**:
   - Repository: `YOUR_USERNAME/YOUR_REPO_NAME`
   - Branch: `main`
   - Main file path: `app.py`
5. **Click**: "Deploy!"

### 3. Configure Secrets (Optional)

For Agentic Mode, you can pre-configure the OpenAI API key:

1. In Streamlit Cloud dashboard, click your app
2. Go to **Settings** → **Secrets**
3. Add:
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

4. Update `app.py` to read from secrets (optional enhancement)

### 4. Important Notes

**Playwright on Streamlit Cloud:**
- ✅ `packages.txt` installs required browser binaries
- ✅ First deployment may take 5-10 minutes (installing Chromium)
- ⚠️ Agentic Mode will be slower due to cloud environment

**Database (SQLite):**
- ✅ Works on Streamlit Cloud
- ⚠️ `users.db` resets on app restarts (ephemeral filesystem)
- 💡 For persistent storage, consider PostgreSQL (future upgrade)

**Login System:**
- ✅ Owner bypass works (detects localhost)
- ✅ Remote users see login screen
- ✅ Quick Signup works (session-only)
- ⚠️ Full Signup accounts lost on restart (use PostgreSQL for persistence)

### 5. Testing Deployment

Once deployed:
1. ✅ Test Free Mode (no API key needed)
2. ✅ Test Agentic Mode (requires OpenAI API key in sidebar)
3. ✅ Test login/signup flow
4. ✅ Upload sample Excel file for bulk processing

### 6. Monitoring

- **Logs**: Available in Streamlit Cloud dashboard
- **Errors**: Check "Manage app" → "Logs"
- **Usage**: Monitor in dashboard

### 7. Custom Domain (Optional)

Streamlit Cloud provides: `your-app-name.streamlit.app`

For custom domain:
1. Upgrade to Streamlit Team/Enterprise
2. Configure DNS CNAME record

## Troubleshooting

**Issue**: Playwright browser not installing
- **Fix**: Check `packages.txt` is in root directory

**Issue**: Database not persisting
- **Fix**: Expected behavior on free tier. Use PostgreSQL for production.

**Issue**: Slow Agentic Mode
- **Fix**: Cloud resources are limited. Use Free Mode for bulk processing.

## Cost Considerations

- Streamlit Cloud: Free tier available
- OpenAI API: Pay per use (GPT-4o ~$0.01-0.03 per extraction)
- Proxy (if used): Varies by provider

## Next Steps

1. Share your app URL with users
2. Monitor usage and errors
3. Consider upgrading to PostgreSQL for persistent accounts
4. Add email service for verification emails (SendGrid, Mailgun)

---

**Need Help?** Check Streamlit Community: https://discuss.streamlit.io
