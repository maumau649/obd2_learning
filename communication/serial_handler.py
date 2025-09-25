"""
Serial-Kommunikation Handler
Verwaltet Arduino-Verbindung und Datenübertragung
"""

import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime
from config.settings import SERIAL_BAUDRATE, SERIAL_TIMEOUT, SERIAL_RECONNECT_INTERVAL

class SerialHandler:
    def __init__(self):
        self.serial = None
        self.running = False
        self.connected = False

        # Callbacks
        self.on_data_received = None
        self.on_connection_changed = None

    def start(self):
        """Startet den Serial-Thread"""
        self.running = True
        self.thread = threading.Thread(target=self._serial_thread, daemon=True)
        self.thread.start()

    def stop(self):
        """Stoppt die Serial-Kommunikation"""
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()

    def send_command(self, command):
        """Sendet einen Befehl an Arduino"""
        if self.serial and self.serial.is_open:
            try:
                self.serial.write((command + "\n").encode())
                self.serial.flush()
                return True
            except Exception as e:
                print(f"Serial Send Error: {e}")
                return False
        return False

    def _serial_thread(self):
        """Hauptthread für Serial-Kommunikation"""
        while self.running:
            if not self.serial or not self.serial.is_open:
                self._try_connect()
                time.sleep(SERIAL_RECONNECT_INTERVAL)
            else:
                self._read_data()
            time.sleep(0.05)

    def _try_connect(self):
        if self.on_connection_changed:
            self.on_connection_changed(False, "Suche Arduino...")

        for port in serial.tools.list_ports.comports():
            try:
                ser = serial.Serial(port.device, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
                time.sleep(3)  # Arduino Boot-Zeit

                # Nur Test-Befehl: STATUS (oder leer)
                ser.write(b"STATUS\n")
                ser.flush()
                time.sleep(0.5)

                # Auf erste Antwort warten
                if ser.in_waiting > 0:
                    # Erfolg: Arduino gefunden
                    self.serial = ser
                    self.connected = True
                    if self.on_connection_changed:
                        self.on_connection_changed(True, f"Verbunden: {port.device}")
                    return
                ser.close()
            except:
                pass

    def _read_data(self):
        """Liest Daten von Arduino"""
        try:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode(errors='ignore').strip()
                if line and self.on_data_received:
                    self.on_data_received(line)

        except Exception as e:
            self.serial = None
            self.connected = False
            if self.on_connection_changed:
                self.on_connection_changed(False, f"Verbindung verloren: {e}")
