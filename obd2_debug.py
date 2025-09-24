"""
KONTINUIERLICHES GAS GEBEN - Erkennt gedrückte Tasten
"""

import serial
import serial.tools.list_ports
import threading
import time
import tkinter as tk
from datetime import datetime

BAUDRATE = 115200

class ContinuousCarGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚗 KONTINUIERLICHE STEUERUNG")
        self.geometry("1000x750")
        self.configure(bg='#000000')

        self.serial = None
        self.running = True

        # Fahrzeugdaten
        self.engine_on = False
        self.rpm = 0
        self.speed = 0
        self.gear = 1
        self.throttle = 0
        self.handbrake = True

        # Tasten-Status für kontinuierliches Drücken
        self.keys_pressed = {
            'gas': False,
            'brake': False,
            'shift_up': False,
            'shift_down': False
        }

        self.create_gui()
        self.bind_keys()

        # Threads
        threading.Thread(target=self.serial_thread, daemon=True).start()
        threading.Thread(target=self.continuous_input_thread, daemon=True).start()

        # Update
        self.update_display()

    def create_gui(self):
        # Header
        header = tk.Frame(self, bg='#1a4c96', height=60)
        header.pack(fill='x', padx=10, pady=5)
        header.pack_propagate(False)

        tk.Label(header, text="🚗 KONTINUIERLICHE AUTO-STEUERUNG", 
                font=('Arial', 18, 'bold'), fg='white', bg='#1a4c96').pack(expand=True)

        # Status
        status_frame = tk.Frame(self, bg='#333333')
        status_frame.pack(fill='x', padx=10, pady=5)

        # Connection
        conn_frame = tk.Frame(status_frame, bg='#333333')
        conn_frame.pack(fill='x', pady=5)

        tk.Label(conn_frame, text="Verbindung:", font=('Arial', 12, 'bold'), 
                fg='white', bg='#333333').pack(side='left')

        self.conn_status = tk.Label(conn_frame, text="🔴 GETRENNT", 
                                   font=('Arial', 12, 'bold'), fg='red', bg='#333333')
        self.conn_status.pack(side='left', padx=10)

        # Tasten-Status Anzeige
        keys_frame = tk.Frame(conn_frame, bg='#333333')
        keys_frame.pack(side='right')

        tk.Label(keys_frame, text="Tasten:", font=('Arial', 10, 'bold'), 
                fg='#cccccc', bg='#333333').pack(side='left')

        self.key_indicators = {}
        key_names = [('gas', '⬆️'), ('brake', '⬇️'), ('shift_up', '➡️'), ('shift_down', '⬅️')]

        for key, symbol in key_names:
            label = tk.Label(keys_frame, text=symbol, font=('Arial', 12, 'bold'), 
                           fg='#666666', bg='#333333')
            label.pack(side='left', padx=2)
            self.key_indicators[key] = label

        # Live-Werte
        values_frame = tk.Frame(self, bg='#1a1a1a')
        values_frame.pack(fill='x', padx=10, pady=10)

        # Motor Status - PROMINENT
        motor_frame = tk.Frame(values_frame, bg='#1a1a1a', bd=3, relief='solid')
        motor_frame.pack(fill='x', pady=5)

        self.engine_label = tk.Label(motor_frame, text="❌ MOTOR AUS", 
                                    font=('Arial', 20, 'bold'), fg='red', bg='#1a1a1a')
        self.engine_label.pack(pady=15)

        # Handbremse
        self.handbrake_label = tk.Label(values_frame, text="🅿️ HANDBREMSE ANGEZOGEN", 
                                       font=('Arial', 16, 'bold'), fg='#ff0000', bg='#1a1a1a')
        self.handbrake_label.pack(pady=10)

        # Hauptwerte - Große Anzeigen
        main_data_frame = tk.Frame(values_frame, bg='#1a1a1a')
        main_data_frame.pack(fill='x', pady=15)

        # RPM - Links
        rpm_frame = tk.Frame(main_data_frame, bg='#2d2d2d', bd=3, relief='solid')
        rpm_frame.pack(side='left', expand=True, fill='both', padx=10)

        tk.Label(rpm_frame, text="DREHZAHL", font=('Arial', 14, 'bold'), 
                fg='white', bg='#2d2d2d').pack(pady=5)
        self.rpm_label = tk.Label(rpm_frame, text="0", font=('Digital-7', 36, 'bold'), 
                                 fg='#00ff00', bg='#2d2d2d')
        self.rpm_label.pack(pady=10)
        tk.Label(rpm_frame, text="U/min", font=('Arial', 12), 
                fg='#cccccc', bg='#2d2d2d').pack(pady=5)

        # Speed - Mitte
        speed_frame = tk.Frame(main_data_frame, bg='#2d2d2d', bd=3, relief='solid')
        speed_frame.pack(side='left', expand=True, fill='both', padx=10)

        tk.Label(speed_frame, text="GESCHWINDIGKEIT", font=('Arial', 14, 'bold'), 
                fg='white', bg='#2d2d2d').pack(pady=5)
        self.speed_label = tk.Label(speed_frame, text="0", font=('Digital-7', 36, 'bold'), 
                                   fg='#0099ff', bg='#2d2d2d')
        self.speed_label.pack(pady=10)
        tk.Label(speed_frame, text="km/h", font=('Arial', 12), 
                fg='#cccccc', bg='#2d2d2d').pack(pady=5)

        # Gang - Rechts
        gear_frame = tk.Frame(main_data_frame, bg='#2d2d2d', bd=3, relief='solid')
        gear_frame.pack(side='right', expand=True, fill='both', padx=10)

        tk.Label(gear_frame, text="GANG", font=('Arial', 14, 'bold'), 
                fg='white', bg='#2d2d2d').pack(pady=5)
        self.gear_label = tk.Label(gear_frame, text="1", font=('Digital-7', 36, 'bold'), 
                                  fg='#ffaa00', bg='#2d2d2d')
        self.gear_label.pack(pady=10)
        tk.Label(gear_frame, text="", font=('Arial', 12), 
                fg='#cccccc', bg='#2d2d2d').pack(pady=5)

        # Gas-Anzeige - Unten
        gas_frame = tk.Frame(values_frame, bg='#2d2d2d', bd=2, relief='solid')
        gas_frame.pack(fill='x', pady=10)

        tk.Label(gas_frame, text="GAS-PEDAL", font=('Arial', 12, 'bold'), 
                fg='white', bg='#2d2d2d').pack(side='left', padx=10, pady=5)

        self.throttle_label = tk.Label(gas_frame, text="0%", font=('Digital-7', 18, 'bold'), 
                                      fg='#ff8800', bg='#2d2d2d')
        self.throttle_label.pack(side='left', padx=20, pady=5)

        # Gas-Balken
        self.throttle_canvas = tk.Canvas(gas_frame, width=300, height=20, bg='#1a1a1a', highlightthickness=0)
        self.throttle_canvas.pack(side='right', padx=10, pady=5)

        self.throttle_bar = self.throttle_canvas.create_rectangle(2, 2, 2, 18, fill='#ff8800')

        # Steuer-Buttons
        control_frame = tk.Frame(self, bg='#333333')
        control_frame.pack(fill='x', padx=10, pady=15)

        tk.Label(control_frame, text="STEUERUNG", font=('Arial', 16, 'bold'), 
                fg='white', bg='#333333').pack(pady=5)

        # Erste Reihe - Motor & Handbremse
        row1 = tk.Frame(control_frame, bg='#333333')
        row1.pack(pady=10)

        self.engine_btn = tk.Button(row1, text="🔥 MOTOR STARTEN", font=('Arial', 14, 'bold'), 
                                   bg='#27ae60', fg='white', command=self.toggle_engine,
                                   width=15, height=2)
        self.engine_btn.pack(side='left', padx=10)

        self.handbrake_btn = tk.Button(row1, text="🅿️ HANDBREMSE LÖSEN", font=('Arial', 14, 'bold'), 
                                      bg='#e74c3c', fg='white', command=self.toggle_handbrake,
                                      width=18, height=2)
        self.handbrake_btn.pack(side='right', padx=10)

        # Zweite Reihe - Fahren
        row2 = tk.Frame(control_frame, bg='#333333')
        row2.pack(pady=5)

        # Gas Button mit speziellem Status
        self.gas_btn = tk.Button(row2, text="⬆️ GAS", font=('Arial', 14, 'bold'), 
                                bg='#f39c12', fg='white', width=10, height=2)
        self.gas_btn.pack(side='left', padx=5)

        self.brake_btn = tk.Button(row2, text="⬇️ BREMSE", font=('Arial', 14, 'bold'), 
                                  bg='#9b59b6', fg='white', width=10, height=2)
        self.brake_btn.pack(side='left', padx=5)

        self.shift_down_btn = tk.Button(row2, text="⬅️ RUNTER", font=('Arial', 14, 'bold'), 
                                       bg='#34495e', fg='white', width=10, height=2)
        self.shift_down_btn.pack(side='left', padx=5)

        self.shift_up_btn = tk.Button(row2, text="➡️ HOCH", font=('Arial', 14, 'bold'), 
                                     bg='#2c3e50', fg='white', width=10, height=2)
        self.shift_up_btn.pack(side='right', padx=5)

        # Anweisungen
        instruction_frame = tk.Frame(control_frame, bg='#333333')
        instruction_frame.pack(pady=10)

        tk.Label(instruction_frame, text="🎮 TASTATUR-STEUERUNG (kontinuierlich)", 
                font=('Arial', 14, 'bold'), fg='#ffff00', bg='#333333').pack()

        tk.Label(instruction_frame, 
                text="P = Motor An/Aus  |  ↑ = Gas (halten möglich!)  |  ↓ = Bremse  |  ← = Runter  |  → = Hoch  |  SPACE = Handbremse", 
                font=('Arial', 11), fg='#cccccc', bg='#333333').pack(pady=5)

        # Logs
        log_container = tk.Frame(self, bg='#444444')
        log_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Gesendete Befehle
        sent_frame = tk.Frame(log_container, bg='#444444')
        sent_frame.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(sent_frame, text="GESENDETE BEFEHLE", font=('Arial', 12, 'bold'), 
                fg='yellow', bg='#444444').pack(anchor='w')

        self.sent_log = tk.Text(sent_frame, height=8, bg='#1a1a1a', fg='#ffff00', 
                               font=('Courier', 9), state='disabled')
        self.sent_log.pack(fill='both', expand=True)

        # Empfangene Daten
        recv_frame = tk.Frame(log_container, bg='#444444')
        recv_frame.pack(side='right', fill='both', expand=True, padx=5)

        tk.Label(recv_frame, text="EMPFANGENE DATEN", font=('Arial', 12, 'bold'), 
                fg='#00ff00', bg='#444444').pack(anchor='w')

        self.recv_log = tk.Text(recv_frame, height=8, bg='#1a1a1a', fg='#00ff00', 
                               font=('Courier', 9), state='disabled')
        self.recv_log.pack(fill='both', expand=True)

    def bind_keys(self):
        """Tastatur-Events für kontinuierliches Drücken"""
        self.focus_set()

        # Motor Toggle
        self.bind('<KeyPress-p>', lambda e: self.toggle_engine())
        self.bind('<KeyPress-P>', lambda e: self.toggle_engine())

        # Handbremse
        self.bind('<KeyPress-space>', lambda e: self.toggle_handbrake())

        # Gas - KeyPress und KeyRelease für kontinuierliches Erkennen
        self.bind('<KeyPress-Up>', self.on_gas_press)
        self.bind('<KeyRelease-Up>', self.on_gas_release)

        # Bremse
        self.bind('<KeyPress-Down>', self.on_brake_press)
        self.bind('<KeyRelease-Down>', self.on_brake_release)

        # Schalten
        self.bind('<KeyPress-Left>', self.on_shift_down_press)
        self.bind('<KeyRelease-Left>', self.on_shift_down_release)

        self.bind('<KeyPress-Right>', self.on_shift_up_press)
        self.bind('<KeyRelease-Right>', self.on_shift_up_release)

    def on_gas_press(self, event):
        """Gas-Taste gedrückt"""
        if not self.keys_pressed['gas']:
            self.keys_pressed['gas'] = True
            self.key_indicators['gas'].config(fg='#00ff00')  # Grün = aktiv
            self.gas_btn.config(bg='#27ae60')  # Grün

    def on_gas_release(self, event):
        """Gas-Taste losgelassen"""
        self.keys_pressed['gas'] = False
        self.key_indicators['gas'].config(fg='#666666')  # Grau = inaktiv
        self.gas_btn.config(bg='#f39c12')  # Orange

    def on_brake_press(self, event):
        """Bremse gedrückt"""
        if not self.keys_pressed['brake']:
            self.keys_pressed['brake'] = True
            self.key_indicators['brake'].config(fg='#ff0000')  # Rot
            self.brake_btn.config(bg='#c0392b')

    def on_brake_release(self, event):
        """Bremse losgelassen"""
        self.keys_pressed['brake'] = False
        self.key_indicators['brake'].config(fg='#666666')
        self.brake_btn.config(bg='#9b59b6')

    def on_shift_up_press(self, event):
        """Hochschalten"""
        if not self.keys_pressed['shift_up']:
            self.keys_pressed['shift_up'] = True
            self.key_indicators['shift_up'].config(fg='#ffaa00')
            self.shift_up_btn.config(bg='#34495e')
            self.send_command("SHIFT_UP")

    def on_shift_up_release(self, event):
        """Hochschalten losgelassen"""
        self.keys_pressed['shift_up'] = False
        self.key_indicators['shift_up'].config(fg='#666666')
        self.shift_up_btn.config(bg='#2c3e50')

    def on_shift_down_press(self, event):
        """Runterschalten"""
        if not self.keys_pressed['shift_down']:
            self.keys_pressed['shift_down'] = True
            self.key_indicators['shift_down'].config(fg='#ffaa00')
            self.shift_down_btn.config(bg='#2c3e50')
            self.send_command("SHIFT_DOWN")

    def on_shift_down_release(self, event):
        """Runterschalten losgelassen"""
        self.keys_pressed['shift_down'] = False
        self.key_indicators['shift_down'].config(fg='#666666')
        self.shift_down_btn.config(bg='#34495e')

    def continuous_input_thread(self):
        """Thread für kontinuierliche Eingabe-Verarbeitung"""
        while self.running:
            # Gas kontinuierlich senden wenn gedrückt
            if self.keys_pressed['gas']:
                self.send_command("THROTTLE")
                time.sleep(0.05)  # 20Hz für flüssiges Gas geben

            # Bremse kontinuierlich senden wenn gedrückt
            if self.keys_pressed['brake']:
                self.send_command("BRAKE")
                time.sleep(0.1)  # 10Hz für Bremse

            # Wenn keine Taste gedrückt, länger warten
            if not any(self.keys_pressed.values()):
                time.sleep(0.1)

    def toggle_engine(self):
        self.send_command("ENGINE_TOGGLE")

    def toggle_handbrake(self):
        self.send_command("HANDBRAKE_TOGGLE")

    def send_command(self, cmd):
        if self.serial and self.serial.is_open:
            try:
                self.serial.write((cmd + "\n").encode())
                self.serial.flush()

                # Nur wichtige Befehle loggen (nicht jeden Throttle)
                if cmd not in ["THROTTLE", "BRAKE"] or len(self.sent_log.get("1.0", "end").strip()) < 500:
                    self.log_sent(f"📤 {cmd}")
            except Exception as e:
                self.log_sent(f"❌ ERROR: {e}")
        else:
            self.log_sent(f"❌ NO CONNECTION: {cmd}")

    def update_throttle_display(self):
        """Gas-Balken aktualisieren"""
        bar_width = int((self.throttle / 100.0) * 296)  # Max 296px Breite

        # Farbe je nach Throttle
        if self.throttle == 0:
            color = '#333333'
        elif self.throttle < 50:
            color = '#ffaa00'
        else:
            color = '#ff0000'

        self.throttle_canvas.coords(self.throttle_bar, 2, 2, 2 + bar_width, 18)
        self.throttle_canvas.itemconfig(self.throttle_bar, fill=color)

    def log_sent(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}\n"

        self.sent_log.config(state='normal')
        self.sent_log.insert('end', entry)
        self.sent_log.see('end')
        self.sent_log.config(state='disabled')

    def log_recv(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}\n"

        self.recv_log.config(state='normal')
        self.recv_log.insert('end', entry)
        self.recv_log.see('end')
        self.recv_log.config(state='disabled')

    def serial_thread(self):
        while self.running:
            if not self.serial or not self.serial.is_open:
                self.conn_status.config(text="🔍 SUCHE...", fg='orange')

                for port in serial.tools.list_ports.comports():
                    try:
                        ser = serial.Serial(port.device, BAUDRATE, timeout=3)
                        time.sleep(3)

                        ser.write(b"ENGINE_TOGGLE\n")
                        ser.flush()
                        time.sleep(0.5)
                        ser.write(b"ENGINE_TOGGLE\n")
                        ser.flush()
                        time.sleep(0.5)

                        response = ""
                        for _ in range(10):
                            if ser.in_waiting > 0:
                                line = ser.readline().decode(errors='ignore').strip()
                                response += line + " "
                                if "SIMULATOR" in line or "ENGINE_RUNNING" in line:
                                    self.serial = ser
                                    self.conn_status.config(text="🟢 VERBUNDEN", fg='green')
                                    self.log_sent(f"✅ Arduino gefunden: {port.device}")
                                    break
                            time.sleep(0.1)

                        if self.serial:
                            break
                        else:
                            ser.close()

                    except Exception:
                        pass

                if not self.serial:
                    time.sleep(2)

            else:
                try:
                    if self.serial.in_waiting > 0:
                        line = self.serial.readline().decode(errors='ignore').strip()
                        if line and not line.startswith("---"):  # Status-Rahmen nicht loggen
                            self.log_recv(line)
                            self.process_line(line)

                except Exception as e:
                    self.serial = None
                    self.conn_status.config(text="🔴 GETRENNT", fg='red')
                    self.log_sent(f"❌ Serial Error: {e}")

            time.sleep(0.05)

    def process_line(self, line):
        if ':' in line:
            try:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key == "ENGINE_RUNNING":
                    self.engine_on = (value == "1")
                elif key == "RPM":
                    self.rpm = int(value)
                elif key == "SPEED":
                    self.speed = int(value)
                elif key == "GEAR":
                    self.gear = int(value)
                elif key == "THROTTLE":
                    self.throttle = int(value)
                elif key == "HANDBRAKE":
                    self.handbrake = (value == "1")

            except (ValueError, IndexError):
                pass

    def update_display(self):
        # Motor
        if self.engine_on:
            self.engine_label.config(text="✅ MOTOR AN", fg='#00ff00')
            self.engine_btn.config(text="🔌 MOTOR STOPPEN", bg='#e74c3c')
        else:
            self.engine_label.config(text="❌ MOTOR AUS", fg='red')
            self.engine_btn.config(text="🔥 MOTOR STARTEN", bg='#27ae60')

        # Handbremse
        if self.handbrake:
            self.handbrake_label.config(text="🅿️ HANDBREMSE ANGEZOGEN", fg='#ff0000')
            self.handbrake_btn.config(text="🚗 HANDBREMSE LÖSEN", bg='#27ae60')
        else:
            self.handbrake_label.config(text="🚗 BEREIT ZUM FAHREN", fg='#00ff00')
            self.handbrake_btn.config(text="🅿️ HANDBREMSE ANZIEHEN", bg='#e74c3c')

        # Werte
        self.rpm_label.config(text=str(self.rpm))
        self.speed_label.config(text=str(self.speed))
        self.gear_label.config(text=str(self.gear))
        self.throttle_label.config(text=f"{self.throttle}%")

        # Gas-Balken
        self.update_throttle_display()

        # Nächstes Update
        self.after(50, self.update_display)

    def on_closing(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.destroy()

if __name__ == "__main__":
    app = ContinuousCarGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()