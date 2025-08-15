# Gem Finder - Development Context

> **VOR JEDER CODE-ÄNDERUNG LESEN!**
> **GRUNDPRINZIP: Minimalinvasive Änderungen - nur explizit Angefordertes!**

---

## KRITISCHE BEREICHE - NIEMALS OHNE ERLAUBNIS ÄNDERN

**VOR jeder Änderung in kritischen Bereichen:**
1. **Erklären** was geändert werden soll
2. **Begründen** warum nötig  
3. **Fragen** um Erlaubnis
4. **Warten** auf Bestätigung

### **GESCHÜTZTE BEREICHE:**
1. **Session State Variablen** - Keine Umbenennungen/neue Variablen
2. **Validierungslogik** - Platform-Mindestanforderungen 
3. **Zweistufige Suchlogik** - Digital → Physical Ablauf
4. **Caching-Verhalten** - Erste Suche cacht, Moduswechsel nutzt Cache

---

## ARCHITEKTUR

### **Streamlit App Structure**
```
Input Mode Selection → Search Form → Results Display
    ├── Manual Input
    ├── Upload Photo (OCR → Fields)
    ├── Take Picture (OCR → Fields)
    └── Multi-Track Support (Semikolon-getrennt)
                    ↓
                Digital Results (iTunes, Beatport, Bandcamp, Traxsource)
                ├── Fragment-basierte Live-Updates
                ├── Mode Switch Button (nur bei digitalen Treffern)
                └── Physical Results (Discogs + Revibed)
                    ├── Gem-GIF + Audio (nur bei Discogs-only)
                    ├── Selenium-Enhanced Marketplace Filtering
                    └── Parallel Offers Processing (5 Browser)
```

### **Such-Flow (KERN-LOGIK)**
```
1. Digital-Validierung OK? → Parallele Suche digitaler Platforms
2. Digitale Treffer? → Zeige + Cache + Mode-Switch Button
3. Keine digitalen? → Auto-Switch zu Physical
4. Physical parallel → Discogs (immer) + Revibed
```

---

## PLATFORM-VALIDIERUNG

### **Digital Platforms** (iTunes, Beatport, Bandcamp, Traxsource)
- Titel + Artist
- Titel + Album
- Artist + Album

**Treffer-Definition für digitale Plattformen:**
- ✅ **Akzent-tolerant**: "Pina" findet "Piña" 
- ✅ **Case-insensitive**: "swag" findet "SWAG"
- ✅ **Teilstring-Match**: "Pina" findet "Pina Colada"
- ✅ **Plattform-spezifische Filterlogik**: iTunes (moderate) vs Beatport (streng)
- ❌ **Keine Satzzeichen-Normalisierung**: "SWAG" ≠ "S.W.A.G."

**Neue Filterlogik (2024-08-04):**
- **iTunes**: Moderate Filterung - mindestens einer der Suchbegriffe muss gefunden werden
- **Beatport**: Strenge wortbasierte Filterung - mindestens ein Wort aus jedem Suchbegriff muss gefunden werden
- **Verhindert**: Irrelevante Matches wie "PICASSO Extended Mix" für "Drum Starts - Picasso"
- **Erlaubt**: Echte Treffer wie "All I Want (Original)" für "Weekender - All I want"

**Relevanz-Scoring-System:**
- **Top 3 Ergebnisse** werden analysiert (statt nur erstes)
- **Scoring-Punkte**: Beide Begriffe = +10, Ein Begriff = +5
- **Bonus-Punkte**: Match im Titel = +3, Exakte Wörter = +2
- **Bestes Ergebnis** wird automatisch ausgewählt
- **Performance-Impact**: +0.1-0.2s pro Plattform (~14% langsamer)

### **Discogs** (Priorität 1-7)
1. Katalognummer + Artist
2. Katalognummer + Album
3. Katalognummer + Titel
4. Titel + Artist
5. Titel + Album
6. Artist + Album
7. Katalognummer (allein)

### **Revibed** (Button-triggered)
- Album OR Artist (eines reicht)
- **Priorität**: Artist > Album (wenn beide ausgefüllt, nur Artist verwenden)
- Suchlogik: Erst Artist prüfen, nur wenn Artist leer dann Album verwenden
- **Ergebnisse**: Bis zu 3 Treffer (statt nur einem)
- **Trigger**: Separater Button "Search on revibed to artist or album"

**Treffer-Definition für Revibed (gleiche Regeln wie digitale Plattformen):**
- ✅ **Akzent-tolerant**: "Pina" findet "Piña" 
- ✅ **Case-insensitive**: "swag" findet "SWAG"
- ✅ **Teilstring-Match**: "Pina" findet "Pina Colada"
- ✅ **Flexible Logik**: Suchbegriff gefunden = Treffer
- ❌ **Keine Satzzeichen-Normalisierung**: "SWAG" ≠ "S.W.A.G."
- **Relevanz-Scoring**: Gleiches System wie digitale Plattformen

---

## ANZEIGE-SZENARIEN

### **Szenario 1: Digitale Treffer**
- Zeige Digital Results
- Mode-Switch Button: "Auf Discogs und Revibed suchen"
- **Cache-Logic**: Erster Klick = echte Suche, weitere = Cache-Abruf

### **Szenario 2: Keine Digital, Revibed OK**
- Auto-Switch zu Physical
- Discogs + Revibed Results
- **Kein** Mode-Switch Button

### **Szenario 3: Nur Discogs**
- Auto-Switch zu Physical  
- **Gem-GIF "You found a real gem"**
- Discogs Results + "Revibed: Keine Treffer"
- **Kein** Mode-Switch Button

---

## PARALLEL-SUCHE

### **Threading-Pattern**
```python
# ThreadPoolExecutor (max 4 Workers) für Digital Search
# as_completed() für Live-Updates pro Platform
# @st.fragment für UI-Updates ohne st.rerun()
# Progress Bar: "iTunes ✅, Beatport ⏳, ..."
# Exception → Error-Message, andere laufen weiter
```

### **Discogs Integration**
```
Release Display:
- Radiobutton List → Detail View (Cover, Jahr, Label, Have/Want)
- "Search for Offers" → Selenium-Enhanced Marketplace
- Parallel Browser Processing (5 Workers)
- Auto-Location Detection → Currency Filtering
- VG+ Filter → Top 5 Results
- Real-time Shipping Availability Check
```

---

## TEST-DUMMIES

### **Trigger-Keywords**
- **Digital**: artist="A" OR track="A" → Dummy für iTunes/Beatport/Bandcamp/Traxsource
- **Physical**: artist="B" OR album contains "b" → Revibed Dummy
- **Discogs**: Gibt IMMER Ergebnisse (laut PRD)

### **Error Handling**
- ImportError/Exception → User-freundliche Fehlermeldung
- Platform als "nicht verfügbar" markieren
- Andere Platforms weiterlaufen lassen

### **Scraper Timeout-Fixes (2024-08-04)**
- **Problem behoben**: Alle Scraper zeigten "nicht verfügbar" statt "Kein Treffer" bei leeren Suchergebnissen
- **Ursache**: WebDriverWait Timeouts bei fehlenden Elementen wurden als technische Fehler behandelt
- **Lösung**: Try-catch Logik unterscheidet "keine Ergebnisse" von "technischen Problemen"
- **Bandcamp**: "name your price" Erkennung für "nyp" statt hardcodierte Preise
- **Alle Plattformen**: Hardcodierte Fallback-Daten entfernt (außer Test-Dummies A/a, B/b)

### **Platform Status & Implementation**
| Platform    | Status    | Implementation      | Trigger         |
|-------------|-----------|---------------------|-----------------|
| iTunes      | Active    | iTunes API (Real)   | artist/track="A"|
| Beatport    | Active    | Selenium Scraper    | artist/track="A"|
| Bandcamp    | Active    | Selenium Scraper    | artist/track="A"|
| Traxsource  | Active    | Selenium Scraper    | artist/track="A"|
| Juno        | Future    | N/A                 | artist/track="A"|
| Soulseek    | Future    | N/A                 | artist/track="A"|
| Revibed     | Active    | Selenium Scraper    | artist="B"/album contains "b"|
| Discogs     | Active    | Discogs API + Selenium Marketplace | Always returns results |

---

## NEUE FEATURES (2024-08-15)

### **Text-Extraktion & OCR**
- **Upload Photo Mode**: Bildupload → OCR → Auto-Fill Felder
- **Take Picture Mode**: Kamera → OCR → Auto-Fill Felder  
- **GPT-4 Vision Integration**: Strukturierte Feldextraktion
- **Mode Context**: Upload=Discogs-Szenario, Camera=Revibed-Szenario
- **File: text_extract.py**

### **Multi-Track Support**
- **Eingabe**: Semikolon-getrennte Track-Liste ("Track1; Track2; Track3")
- **UI**: Dropdown-Auswahl + Dedicated Search Button pro Track
- **Cache-Logik**: Cache ohne Track-Name für Effizienz
- **Performance**: Nur ein API-Call für alle Tracks

### **Fragment-basierte UI**
- **@st.fragment**: Live-Updates ohne st.rerun() für bessere Performance
- **show_live_results()**: Progressive Anzeige während Parallel-Search
- **show_offers_fragment()**: Event-basierte Offers-Updates
- **show_revibed_fragment()**: Parallel Revibed Loading

### **Performance-Optimierungen**
- **IPv4-Only**: Für iTunes/Discogs API (vermeidet IPv6 Timeouts)
- **Selenium Parallel Processing**: 5 Browser gleichzeitig für Offers
- **Connection Pooling**: Session-Reuse für iTunes API
- **Early Exit Strategies**: Stoppe bei genug Ergebnissen

### **Selenium-Enhanced Marketplace**
- **Shipping Validation**: Real-time Check per Browser
- **Currency Filtering**: Auto-Location → Preferred Currency  
- **Parallel Workers**: 5 Browser für Maximum Speed
- **Condition Filtering**: VG+/NM/M Quality Toggle
- **File: selenium_scraper.py**

### **Audio & Visual Enhancements**
- **Real Gem Audio**: MP3 Applause bei Discogs-only Finds
- **Scroll Preservation**: JavaScript für stabile UI
- **Progressive Loading**: Live Status Updates
- **Improved Icons**: Platform-spezifische Visuals

---

## ENTWICKLUNGS-TIPPS

- Parallel API-Calls mit ThreadPoolExecutor
- @st.fragment für Live-Updates ohne st.rerun()
- @st.cache_data für API-Responses  
- Session State für Input-Persistence
- IPv4-Optimierung für API-Performance
- Selenium Parallel Processing für Marketplace

---

**Bei Architektur-Änderungen: Diese Datei entsprechend updaten!**