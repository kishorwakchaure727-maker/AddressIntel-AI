# Streamlit Deployment Quick Start

## Local Testing

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up secrets (for local development):**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your OpenAI API key
```

3. **Run the app locally:**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
# Ensure you're in the repo directory
cd /workspaces/AddressIntel-AI

# Initialize git (if not already done)
git add .
git commit -m "Add Streamlit configuration for deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Configure:
   - **Repository**: `YOUR_USERNAME/AddressIntel-AI`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Deploy!"**

The app will deploy in a few minutes.

### Step 3: Add Secrets in Streamlit Cloud

1. Go to your app on Streamlit Cloud
2. Click the **≡** (menu) → **Settings**
3. Go to **Secrets**
4. Add your secrets in TOML format:
```toml
OPENAI_API_KEY = "sk-..."
```
5. Save and the app will restart with the new secrets

---

## System Dependencies

The `packages.txt` file ensures system-level dependencies (like Playwright) are installed:
- `libgbm1` - For headless browser rendering

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error for `playwright` | Ensure `packages.txt` exists with required system packages |
| OpenAI API errors | Check that `OPENAI_API_KEY` is set in Streamlit Secrets |
| Browser crashes | May need to update Playwright: `pip install --upgrade playwright` |
| Timeout errors | Increase timeout in agent_logic.py or check network connectivity |

---

## Environment Variables

Your app uses the following secrets (in `.streamlit/secrets.toml`):
- `OPENAI_API_KEY` - Your OpenAI API key for AI extraction

---

## File Structure

```
AddressIntel-AI/
├── app.py                        # Main Streamlit app
├── agent_logic.py                # AI extraction logic
├── user_db.py                    # User database
├── requirements.txt              # Python dependencies
├── packages.txt                  # System dependencies (APT packages)
├── .streamlit/
│   ├── config.toml              # Streamlit configuration
│   └── secrets.toml.example     # Example secrets file
├── README.md
└── DEPLOYMENT.md
```

---

## References

- [Streamlit Cloud Docs](https://docs.streamlit.io/deploy)
- [Secrets Management](https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app/secrets-management)
