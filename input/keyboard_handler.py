"""
Tastatur-Eingaben Handler
Verwaltet kontinuierliche Tasteneingaben
"""

import threading
import time
from config.settings import KEY_INPUT_RATE

class KeyboardHandler:
    def __init__(self, gui_window):
        self.window = gui_window
        self.running = False

        # Tastenstatus
        self.keys_pressed = {
            'gas': False,
            'brake': False,
            'shift_up': False,
            'shift_down': False
        }

        # Callbacks
        self.on_gas_continuous = None
        self.on_brake_continuous = None

        self._bind_keys()

    def start(self):
        """Startet kontinuierliche Eingabe-Verarbeitung"""
        self.running = True
        self.thread = threading.Thread(target=self._continuous_input_thread, daemon=True)
        self.thread.start()

    def stop(self):
        """Stoppt Eingabe-Verarbeitung"""
        self.running = False

    def _bind_keys(self):
        """Bindet Tastatur-Events"""
        # Motor
        self.window.bind('<KeyPress-p>', lambda e: self._on_engine_toggle())
        self.window.bind('<KeyPress-P>', lambda e: self._on_engine_toggle())

        # Gas - kontinuierlich
        self.window.bind('<KeyPress-Up>', self._on_gas_press)
        self.window.bind('<KeyRelease-Up>', self._on_gas_release)

        # Bremse - kontinuierlich
        self.window.bind('<KeyPress-Down>', self._on_brake_press)
        self.window.bind('<KeyRelease-Down>', self._on_brake_release)

        # Schalten - einmalig
        self.window.bind('<KeyPress-Left>', self._on_shift_down)
        self.window.bind('<KeyPress-Right>', self._on_shift_up)

    def _on_engine_toggle(self):
        """Motor an/aus"""
        if hasattr(self.window, 'toggle_engine'):
            self.window.toggle_engine()

    def _on_gas_press(self, event):
        """Gas-Taste gedrückt"""
        if not self.keys_pressed['gas']:
            self.keys_pressed['gas'] = True
            if hasattr(self.window, 'on_gas_press'):
                self.window.on_gas_press()

    def _on_gas_release(self, event):
        """Gas-Taste losgelassen"""
        self.keys_pressed['gas'] = False
        if hasattr(self.window, 'on_gas_release'):
            self.window.on_gas_release()

    def _on_brake_press(self, event):
        """Bremse gedrückt"""
        if not self.keys_pressed['brake']:
            self.keys_pressed['brake'] = True
            if hasattr(self.window, 'on_brake_press'):
                self.window.on_brake_press()

    def _on_brake_release(self, event):
        """Bremse losgelassen"""
        self.keys_pressed['brake'] = False
        if hasattr(self.window, 'on_brake_release'):
            self.window.on_brake_release()

    def _on_shift_up(self, event):
        """Hochschalten"""
        if hasattr(self.window, 'shift_up'):
            self.window.shift_up()

    def _on_shift_down(self, event):
        """Runterschalten"""
        if hasattr(self.window, 'shift_down'):
            self.window.shift_down()

    def _continuous_input_thread(self):
        """Thread für kontinuierliche Eingaben"""
        while self.running:
            # Gas kontinuierlich
            if self.keys_pressed['gas'] and self.on_gas_continuous:
                self.on_gas_continuous()

            # Bremse kontinuierlich
            if self.keys_pressed['brake'] and self.on_brake_continuous:
                self.on_brake_continuous()

            # Pause je nach Aktivität
            if any(self.keys_pressed.values()):
                time.sleep(KEY_INPUT_RATE / 1000.0)  # ms zu s
            else:
                time.sleep(0.1)  # Längere Pause wenn keine Taste gedrückt
