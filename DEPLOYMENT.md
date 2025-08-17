# GemFinder - Streamlit Cloud Deployment Guide

## Quick Start für Streamlit Cloud

### 1. Repository Setup
```bash
git add .
git commit -m "Add Streamlit Cloud deployment files"
git push origin main
```

### 2. Streamlit Cloud Deployment

1. Gehe zu [share.streamlit.io](https://share.streamlit.io)
2. Login mit GitHub Account
3. "New app" → Repository auswählen: `TimoTurner/GemFinder`
4. **WICHTIG**: Main file path: `main_deployment.py` (nicht main.py!)
5. Advanced settings:
   - Python version: 3.9+
   - Add secrets (siehe unten)

### 3. Secrets Configuration in Streamlit Cloud

In der Streamlit Cloud Console → App Settings → Secrets:

```toml
# OpenAI API Key für OCR/Text-Extraktion
OPENAI_API_KEY = "sk-..."

# Optional: Custom User Agent
USER_AGENT = "GemFinder/1.0 Music Discovery App"
```

### 4. Files Overview

**Deployment Files (für Streamlit Cloud):**
- `main_deployment.py` - Hauptapp mit Cloud-Anpassungen
- `selenium_scraper_deployment.py` - Selenium mit Chromium-Support
- `ui_helpers_deployment.py` - UI mit Deployment-Imports
- `requirements_deployment.txt` - Dependencies
- `packages.txt` - System packages (Chromium)
- `.streamlit/config.toml` - Streamlit Konfiguration

**Original Files (für lokale Entwicklung):**
- `main.py` - Original Hauptapp
- `selenium_scraper.py` - Original Selenium
- `ui_helpers.py` - Original UI helpers
- `requirements.txt` - Original requirements

### 5. Features Verfügbar in Cloud

✅ **Vollständig funktionsfähig:**
- Digital Search (iTunes, Beatport, Bandcamp, Traxsource)
- Discogs API Search
- Revibed Scraping  
- OCR Text-Extraktion (Upload/Camera)
- Multi-Track Support
- Selenium Marketplace Scraping

✅ **Performance:**
- 2-5s Response Time für einzelne User
- Zeitlich verteilte Nutzung optimal
- Automatic Browser Management

### 6. Monitoring & Debugging

**Logs ansehen:**
- Streamlit Cloud Console → Logs Tab
- Selenium-Fehler werden geloggt
- Browser-Crashes sichtbar

**Common Issues:**
- Chromium nicht gefunden → packages.txt korrekt?
- OpenAI API Fehler → Secrets korrekt gesetzt?
- Selenium Timeout → Normale Schwankung bei Cloud-Servern

### 7. Updates Deployen

```bash
# Änderungen an Deployment-Files
git add *_deployment.py
git commit -m "Update deployment version"
git push origin main
# → Automatisches Redeployment in ~2-3 Minuten
```

### 8. Rollback Plan

Falls Deployment-Probleme:
1. Git Branch wechseln zu stabiler Version
2. Oder: main.py zu main_deployment.py umbenennen (Original-Code)

---

**Status: ✅ Bereit für Streamlit Cloud Deployment**