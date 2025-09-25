
import tkinter as tk
from datetime import datetime

# Lokale Imports
from models.vehicle import Vehicle
from communication.serial_handler import SerialHandler
from input.keyboard_handler import KeyboardHandler
from config.settings import *

class CarDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        # Fenster-Konfiguration
        self.title("Fahrzeug-Simulator Dashboard")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(bg=COLORS['background'])

        # Datenmodell
        self.vehicle = Vehicle()

        # Kommunikation
        self.serial_handler = SerialHandler()
        self.serial_handler.on_data_received = self.process_serial_data
        self.serial_handler.on_connection_changed = self.on_connection_changed

        # Eingaben
        self.keyboard_handler = KeyboardHandler(self)
        self.keyboard_handler.on_gas_continuous = lambda: self.send_command("THROTTLE")
        self.keyboard_handler.on_brake_continuous = lambda: self.send_command("BRAKE")

        # GUI erstellen
        self.create_gui()

        # Starten
        self.serial_handler.start()
        self.keyboard_handler.start()
        self.update_display()

        # Schließen-Handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_gui(self):
        # Header
        header = tk.Frame(self, bg=COLORS['accent'], height=60)
        header.pack(fill='x', padx=10, pady=5)
        header.pack_propagate(False)
        tk.Label(
            header,
            text="FAHRZEUG-SIMULATOR",
            font=('Arial', 18, 'bold'),
            fg=COLORS['text_white'],
            bg=COLORS['accent']
        ).pack(expand=True)

        # Status-Leiste
        status_frame = tk.Frame(self, bg='#333333')
        status_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(
            status_frame, text="Verbindung:",
            font=('Arial', 12, 'bold'),
            fg=COLORS['text_white'], bg='#333333'
        ).pack(side='left')
        self.conn_status = tk.Label(
            status_frame, text="GETRENNT",
            font=('Arial', 12, 'bold'),
            fg=COLORS['error'], bg='#333333'
        )
        self.conn_status.pack(side='left', padx=10)
        self._create_key_indicators(status_frame)

        # Hauptanzeigen
        self._create_main_displays()

        # Steuer-Buttons
        self._create_controls()

        # Logs
        self._create_logs()

    def _create_key_indicators(self, parent):
        keys_frame = tk.Frame(parent, bg='#333333')
        keys_frame.pack(side='right')
        tk.Label(
            keys_frame, text="Tasten:",
            font=('Arial', 10, 'bold'),
            fg=COLORS['text_gray'], bg='#333333'
        ).pack(side='left')
        self.key_indicators = {}
        for key, symbol in [('gas', '⬆️'), ('brake', '⬇️')]:
            lbl = tk.Label(
                keys_frame, text=symbol,
                font=('Arial', 12, 'bold'),
                fg='#666666', bg='#333333'
            )
            lbl.pack(side='left', padx=2)
            self.key_indicators[key] = lbl

    def _create_main_displays(self):
        main_frame = tk.Frame(self, bg=COLORS['panel'])
        main_frame.pack(fill='x', padx=10, pady=10)

        # Motor Status
        self.engine_label = tk.Label(
            main_frame, text="MOTOR AUS",
            font=('Arial', 20, 'bold'),
            fg=COLORS['error'], bg=COLORS['panel']
        )
        self.engine_label.pack(pady=15)

        # Werte
        values_frame = tk.Frame(main_frame, bg=COLORS['panel'])
        values_frame.pack(fill='x', pady=15)
        self.rpm_label = self._value_label(values_frame, "DREHZAHL", "U/min")
        self.speed_label = self._value_label(values_frame, "GESCHWINDIGKEIT", "km/h")
        self.gear_label = self._value_label(values_frame, "GANG", "")
        self._create_throttle_display(main_frame)
        self.shift_indicator = tk.Label(
            main_frame, text="", font=('Arial', 14, 'bold'),
            fg=COLORS['warning'], bg=COLORS['panel']
        )
        self.shift_indicator.pack(pady=10)

    def _value_label(self, parent, title, unit):
        frame = tk.Frame(parent, bg='#2d2d2d', bd=3, relief='solid')
        frame.pack(side='left', expand=True, fill='both', padx=10)
        tk.Label(
            frame, text=title,
            font=('Arial', 14, 'bold'),
            fg=COLORS['text_white'], bg='#2d2d2d'
        ).pack(pady=5)
        val_lbl = tk.Label(
            frame, text="0",
            font=('Arial', 36, 'bold'),
            fg=COLORS['success'] if title=="DREHZAHL" else COLORS['info'],
            bg='#2d2d2d'
        )
        val_lbl.pack(pady=10)
        tk.Label(
            frame, text=unit,
            font=('Arial', 12),
            fg=COLORS['text_gray'], bg='#2d2d2d'
        ).pack(pady=5)
        return val_lbl

    def _create_throttle_display(self, parent):
        gas_frame = tk.Frame(parent, bg='#2d2d2d', bd=2, relief='solid')
        gas_frame.pack(fill='x', pady=10)
        tk.Label(
            gas_frame, text="GAS-PEDAL",
            font=('Arial', 12, 'bold'),
            fg=COLORS['text_white'], bg='#2d2d2d'
        ).pack(side='left', padx=10, pady=5)
        self.throttle_label = tk.Label(
            gas_frame, text="0%",
            font=('Arial', 18, 'bold'),
            fg=COLORS['warning'], bg='#2d2d2d'
        )
        self.throttle_label.pack(side='left', padx=20, pady=5)
        self.throttle_canvas = tk.Canvas(
            gas_frame, width=300, height=20,
            bg=COLORS['background'], highlightthickness=0
        )
        self.throttle_canvas.pack(side='right', padx=10, pady=5)
        self.throttle_bar = self.throttle_canvas.create_rectangle(
            2, 2, 2, 18, fill=COLORS['warning']
        )

    def _create_controls(self):
        ctrl = tk.Frame(self, bg='#333333')
        ctrl.pack(fill='x', padx=10, pady=15)
        tk.Label(
            ctrl, text="STEUERUNG",
            font=('Arial', 16, 'bold'),
            fg=COLORS['text_white'], bg='#333333'
        ).pack(pady=5)
        btn_frame = tk.Frame(ctrl, bg='#333333')
        btn_frame.pack(pady=10)
        self.engine_btn = tk.Button(
            btn_frame, text="MOTOR STARTEN",
            font=('Arial', 14, 'bold'),
            bg='#27ae60', fg='white',
            command=lambda: self.send_command("ENGINE_TOGGLE"),
            width=15, height=2
        )
        self.engine_btn.pack(side='left', padx=10)
        tk.Button(
            btn_frame, text="⬆GAS",
            font=('Arial', 12, 'bold'),
            bg='#f39c12', fg='white',
            width=8, height=2
        ).pack(side='left', padx=5)
        tk.Button(
            btn_frame, text="⬇BREMSE",
            font=('Arial', 12, 'bold'),
            bg='#9b59b6', fg='white',
            width=8, height=2
        ).pack(side='left', padx=5)
        tk.Button(
            btn_frame, text="⬅RUNTER",
            font=('Arial', 12, 'bold'),
            bg='#34495e', fg='white',
            width=8, height=2,
            command=lambda: self.send_command("SHIFT_DOWN")
        ).pack(side='left', padx=5)
        tk.Button(
            btn_frame, text="HOCH",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50', fg='white',
            width=8, height=2,
            command=lambda: self.send_command("SHIFT_UP")
        ).pack(side='right', padx=5)
        tk.Label(
            ctrl,
            text="P = Motor  |  ↑ = Gas (halten!)  |  ↓ = Bremse  |  ← = Runter  |  → = Hoch",
            font=('Arial', 11),
            fg=COLORS['text_gray'], bg='#333333'
        ).pack(pady=5)

    def _create_logs(self):
        log_container = tk.Frame(self, bg='#444444')
        log_container.pack(fill='both', expand=True, padx=10, pady=10)
        sent_frame = tk.Frame(log_container, bg='#444444')
        sent_frame.pack(side='left', fill='both', expand=True, padx=5)
        tk.Label(
            sent_frame, text="GESENDETE BEFEHLE",
            font=('Arial', 12, 'bold'),
            fg='yellow', bg='#444444'
        ).pack(anchor='w')
        self.sent_log = tk.Text(
            sent_frame, height=6,
            bg=COLORS['background'], fg='#ffff00',
            font=('Courier', 9), state='disabled'
        )
        self.sent_log.pack(fill='both', expand=True)
        recv_frame = tk.Frame(log_container, bg='#444444')
        recv_frame.pack(side='right', fill='both', expand=True, padx=5)
        tk.Label(
            recv_frame, text="EMPFANGENE DATEN",
            font=('Arial', 12, 'bold'),
            fg=COLORS['success'], bg='#444444'
        ).pack(anchor='w')
        self.recv_log = tk.Text(
            recv_frame, height=6,
            bg=COLORS['background'], fg=COLORS['success'],
            font=('Courier', 9), state='disabled'
        )
        self.recv_log.pack(fill='both', expand=True)

    def send_command(self, cmd):
        success = self.serial_handler.send_command(cmd)
        if success:
            self._log(self.sent_log, f"{cmd}")
        else:
            self._log(self.sent_log, f"{cmd} (keine Verbindung)")

    def process_serial_data(self, line):
        if not line.startswith("---"):
            self._log(self.recv_log, line)
        if ':' in line:
            key, value = line.split(':', 1)
            self.vehicle.update_from_data(key.strip(), value.strip())

    def on_connection_changed(self, connected, message):
        self.conn_status.config(
            text="VERBUNDEN" if connected else "GETRENNT",
            fg=COLORS['success'] if connected else COLORS['error']
        )
        self._log(self.sent_log, message)

    def update_display(self):
        # Motor Status
        if self.vehicle.engine_running:
            self.engine_label.config(text="MOTOR AN", fg=COLORS['success'])
            self.engine_btn.config(text="MOTOR STOPPEN", bg='#e74c3c')
        else:
            self.engine_label.config(text="MOTOR AUS", fg=COLORS['error'])
            self.engine_btn.config(text="MOTOR STARTEN", bg='#27ae60')

        # Werte
        self.rpm_label.config(
            text=str(self.vehicle.rpm),
            fg=self.vehicle.get_rpm_color()
        )
        self.speed_label.config(text=str(self.vehicle.speed))
        self.gear_label.config(text=str(self.vehicle.gear))
        self.throttle_label.config(text=f"{self.vehicle.throttle}%")
        self._update_throttle_bar()

        # Schaltempfehlung
        self.shift_indicator.config(
            text=self.vehicle.get_shift_recommendation()
        )

        # Next update
        self.after(GUI_UPDATE_RATE, self.update_display)

    def _update_throttle_bar(self):
        bar_width = int((self.vehicle.throttle / 100.0) * 296)
        color = (
            COLORS['warning'] if self.vehicle.throttle < 50
            else COLORS['error'] if self.vehicle.throttle > 50
            else '#333333'
        )
        self.throttle_canvas.coords(self.throttle_bar, 2, 2, 2 + bar_width, 18)
        self.throttle_canvas.itemconfig(self.throttle_bar, fill=color)

    def _log(self, widget, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}\n"
        widget.config(state='normal')
        widget.insert('end', entry)
        widget.see('end')
        widget.config(state='disabled')

    def on_closing(self):
        self.serial_handler.stop()
        self.keyboard_handler.stop()
        self.destroy()