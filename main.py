"""
Hauptprogramm - Startet die Auto-Simulator GUI
"""

import sys
import os

# Lokale Module importieren
from gui.dashboard import CarDashboard

def main():
    """Startet die Fahrzeug-Simulator Anwendung"""
    print("Starte Fahrzeug-Simulator...")

    try:
        app = CarDashboard()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAnwendung beendet")
    except Exception as e:
        print(f"Fehler beim Starten: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
