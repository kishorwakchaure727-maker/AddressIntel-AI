# AddressIntel AI

**Intelligent Corporate Location Intelligence** - AI-powered address extraction from company websites.

## Features

- **Dual Extraction Modes**:
  - **Free Mode**: Fast regex-based extraction
  - **Agentic Mode**: AI-powered browser automation with GPT-4o
  
- **Dual Signup System**:
  - **Quick Signup**: Session-only, instant access
  - **Full Signup**: Persistent accounts with email verification
  
- **Input Options**:
  - Single company entry
  - Bulk Excel upload
  
- **Smart Extraction**:
  - Extracts from maps and dropdowns
  - Web search fallback for missing information
  - Structured output (Street, City, State, PIN, Country)

## Deployment

Deployed on Streamlit Cloud. Visit: [Your App URL Here]

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Run the app:
```bash
streamlit run app.py
```

## Configuration

- **Owner Bypass**: Owner (localhost) automatically bypasses login
- **OpenAI API Key**: Required for Agentic Mode (set in sidebar or secrets)
- **Proxy Support**: Optional for high-volume processing

## Tech Stack

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-4o
- **Browser Automation**: Playwright
- **Database**: SQLite (for user accounts)
- **Web Scraping**: BeautifulSoup4, Requests
