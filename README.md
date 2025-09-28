# Fahrzeug-Simulator

## Installation & Start

### 1. Arduino vorbereiten
```bash
# Arduino Code hochladen:
obd2_learning.ino
```

### 2. Python-Abhängigkeiten
```bash
pip install pyserial
```

### 3. Programm starten
```bash
python main.py
```

## Steuerung

- **P** = Motor an/aus
- **↑** = Gas geben (halten möglich!)
- **↓** = Bremsen
- **←** = Runterschalten
- **→** = Hochschalten

## Features
**Kontinuierliches Gas** - Taste halten = dauerhaft Gas
**Modulare Struktur** - Übersichtlicher Code
**Sofortige RPM-Reaktion** - Kein Lag
**5-Gang Schaltung** - Realistische Übersetzungen
**Farbcodierte RPM** - Grün → Gelb → Orange → Rot

## Konfiguration
Alle Einstellungen in `config/settings.py`:
- Update-Raten
- Farben
- RPM-Bereiche
- Serial-Parameter

## RPM-Bereiche
- **0-800**: Motor aus/Leerlauf
- **800-3000**: Normaler Betrieb (Grün)
- **3000-5000**: Sportlich (Gelb)
- **5000-6500**: Hoch (Orange)
- **6500-7000**: Redline (Rot)
