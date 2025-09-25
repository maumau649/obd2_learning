"""
Fahrzeug-Datenmodell
Verwaltet alle Fahrzeugdaten und Status
"""

from config.settings import ENGINE_IDLE_RPM, ENGINE_MAX_RPM, ENGINE_REDLINE_RPM, MAX_SPEED, MAX_GEARS

class Vehicle:
    def __init__(self):
        # Grunddaten
        self.engine_running = False
        self.rpm = 0
        self.speed = 0
        self.gear = 1
        self.throttle = 0

        # Status
        self.rpm_status = "OK"

        # Eingaben (von GUI gesteuert)
        self.gas_pressed = False
        self.brake_pressed = False

    def update_from_data(self, key, value):
        """Aktualisiert Fahrzeugdaten von Serial-Input"""
        try:
            if key == "ENGINE_RUNNING":
                self.engine_running = (value == "1")
            elif key == "RPM":
                self.rpm = int(value)
            elif key == "SPEED":
                self.speed = int(value)
            elif key == "GEAR":
                self.gear = int(value)
            elif key == "THROTTLE":
                self.throttle = int(value)
            elif key == "RPM_STATUS":
                self.rpm_status = value
        except (ValueError, IndexError):
            pass

    def get_rpm_color(self):
        """Gibt Farbe für RPM-Anzeige zurück"""
        if self.rpm == 0:
            return '#555555'
        elif self.rpm < 3000:
            return '#00ff00'  # Grün
        elif self.rpm < 5000:
            return '#ffaa00'  # Gelb
        elif self.rpm < ENGINE_REDLINE_RPM:
            return '#ff8800'  # Orange
        else:
            return '#ff0000'  # Rot

    def get_shift_recommendation(self):
        """Gibt Schaltempfehlung zurück"""
        if self.rpm_status == "SHIFT_UP":
            return "HOCHSCHALTEN"
        elif self.rpm_status == "SHIFT_DOWN":
            return "⬇RUNTERSCHALTEN"
        elif self.rpm_status == "REDLINE":
            return "REDLINE!"
        elif self.rpm_status == "HIGH":
            return "HOHE DREHZAHL"
        else:
            return ""

    def can_start_engine(self):
        """Prüft ob Motor gestartet werden kann"""
        return not self.engine_running and self.speed == 0

    def can_stop_engine(self):
        """Prüft ob Motor gestoppt werden kann"""
        return self.engine_running and self.speed == 0

    def can_shift_up(self):
        """Prüft ob hochgeschaltet werden kann"""
        return self.engine_running and self.gear < MAX_GEARS and self.rpm >= 1500

    def can_shift_down(self):
        """Prüft ob runtergeschaltet werden kann"""
        return self.engine_running and self.gear > 1

    def __str__(self):
        """String-Repräsentation für Debugging"""
        return f"Engine: {self.engine_running}, RPM: {self.rpm}, Speed: {self.speed}, Gear: {self.gear}"
