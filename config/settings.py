"""
Konfiguration für den Fahrzeug-Simulator
"""

# Serial Kommunikation
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 3
SERIAL_RECONNECT_INTERVAL = 2.0

# GUI Update-Raten
GUI_UPDATE_RATE = 50        # ms - Hauptdisplay
SERIAL_READ_RATE = 50       # ms - Serial lesen
KEY_INPUT_RATE = 50         # ms - Gas kontinuierlich

# Fahrzeug-Parameter
ENGINE_IDLE_RPM = 850
ENGINE_MAX_RPM = 7000
ENGINE_REDLINE_RPM = 6500
MAX_SPEED = 200
MAX_GEARS = 5

# Farben (Hex)
COLORS = {
    'background': '#000000',
    'panel': '#1a1a1a',
    'accent': '#1a4c96',
    'text_white': '#ffffff',
    'text_gray': '#cccccc',
    'success': '#00ff00',
    'warning': '#ffaa00',
    'error': '#ff0000',
    'info': '#0099ff'
}

# GUI Dimensionen
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1080

# Debug-Modus
DEBUG_MODE = True
LOG_SERIAL_DATA = True
