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
Search Form → Results Display
                ├── Digital Results (iTunes, Beatport, Bandcamp, Traxsource)
                ├── Mode Switch Button (nur bei digitalen Treffern)
                └── Physical Results (Discogs + Revibed)
                    ├── Gem-GIF (nur bei Discogs-only)
                    └── Marketplace (nach Button + Standort)
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
- ✅ **Flexible AND-Logik**: Artist OR Track gefunden = Treffer
- ❌ **Keine Satzzeichen-Normalisierung**: "SWAG" ≠ "S.W.A.G."

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

### **Revibed**
- Album OR Artist (eines reicht)
- **Priorität**: Artist > Album (wenn beide ausgefüllt, nur Artist verwenden)
- Suchlogik: Erst Artist prüfen, nur wenn Artist leer dann Album verwenden

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
# ThreadPoolExecutor (max 4 Workers)
# as_completed() für Live-Updates pro Platform
# st.empty() Container für UI-Updates (KEIN st.rerun!)
# Progress Bar: "iTunes ✅, Beatport ⏳, ..."
# Exception → Error-Message, andere laufen weiter
```

### **Discogs Integration**
```
Release Display:
- Radiobutton List → Detail View (Cover, Jahr, Label, Have/Want)
- "Angebote suchen" → Standort → Marketplace (VG+/NM/M, top 10)
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

### **Platform Status**
| Platform    | Status    | Trigger         |
|-------------|-----------|-----------------|
| iTunes      | Active    | artist/track="A"|
| Beatport    | Active    | artist/track="A"|
| Bandcamp    | Active    | artist/track="A"|
| Traxsource  | Active    | artist/track="A"|
| Juno        | Future    | artist/track="A"|
| Soulseek    | Future    | artist/track="A"|
| Revibed     | Active    | artist="B"/album contains "b"|
| Discogs     | Active    | Always returns results |

---

## ENTWICKLUNGS-TIPPS

- Parallel API-Calls mit ThreadPoolExecutor
- @st.cache_data für API-Responses  
- Session State für Input-Persistence
- Minimaler st.rerun() Einsatz

---

**Bei Architektur-Änderungen: Diese Datei entsprechend updaten!**