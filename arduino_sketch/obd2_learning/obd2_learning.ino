/*
 * FAHRZEUG-SIMULATOR OHNE HANDBREMSE
 * Mit Status-LEDs auf PIN 12 (SENDER) und PIN 13 (RECEIVER)
 */

#include <SPI.h>
#include <mcp_can.h>

// Hardware
#define SENDER_CS_PIN    53
#define RECEIVER_CS_PIN  49
#define LED_SENDER       12  // externer Sender-Indikator
#define LED_RECEIVER     13  // externer Receiver-Indikator

MCP_CAN CAN0(SENDER_CS_PIN);
MCP_CAN CAN1(RECEIVER_CS_PIN);

// Fahrzeug-Zustand
bool engine_on = false;
int rpm = 0;
int target_rpm = 0;
int speed = 0;
int gear = 1;
int throttle = 0;
bool gas_pressed = false;
bool brake_pressed = false;

// Timing
unsigned long last_rpm_update  = 0;
unsigned long last_status_send = 0;
unsigned long last_gas_command = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // LED-Pins
  pinMode(LED_SENDER, OUTPUT);
  pinMode(LED_RECEIVER, OUTPUT);
  digitalWrite(LED_SENDER, LOW);
  digitalWrite(LED_RECEIVER, LOW);

  SPI.begin();
  CAN0.begin(MCP_STDEXT, CAN_500KBPS, MCP_8MHZ);
  CAN0.setMode(MCP_NORMAL);
  CAN1.begin(MCP_STDEXT, CAN_500KBPS, MCP_8MHZ);
  CAN1.setMode(MCP_NORMAL);

  Serial.println();
  Serial.println("=== FAHRZEUG-SIMULATOR (OHNE HANDBREMSE) ===");
  Serial.println("Befehle: ENGINE_TOGGLE, THROTTLE, BRAKE, SHIFT_UP, SHIFT_DOWN");
  Serial.println("==========================================");
  Serial.println();

  sendStatus();
}

void loop() {
  unsigned long now = millis();

  processCommands();

  // RPM-Updates alle 20 ms
  if (now - last_rpm_update >= 20) {
    updateRPM();
    last_rpm_update = now;
  }

  // Status alle 100 ms
  if (now - last_status_send >= 100) {
    sendStatus();
    last_status_send = now;
  }

  // Gas-Timeout
  if (now - last_gas_command > 200 && gas_pressed) {
    gas_pressed = false;
    Serial.println(">>> Gas losgelassen (Timeout)");
  }

  delay(10);
}

void processCommands() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "ENGINE_TOGGLE") toggleEngine();
    else if (cmd == "THROTTLE")  handleThrottle();
    else if (cmd == "BRAKE")     handleBrake();
    else if (cmd == "SHIFT_UP")  shiftUp();
    else if (cmd == "SHIFT_DOWN")shiftDown();
  }
}

void toggleEngine() {
  if (!engine_on) {
    engine_on = true;
    rpm = 850; target_rpm = 850; gear = 1;
    Serial.println("*** MOTOR GESTARTET! RPM: 850 ***");
    digitalWrite(LED_SENDER, HIGH);
    delay(50);
    digitalWrite(LED_SENDER, LOW);
  } else {
    if (speed == 0) {
      engine_on = false; rpm = target_rpm = throttle = 0; gas_pressed = false;
      Serial.println("*** MOTOR GESTOPPT! ***");
      digitalWrite(LED_RECEIVER, HIGH);
      delay(50);
      digitalWrite(LED_RECEIVER, LOW);
    } else {
      Serial.println(">>> Motor Stop fehlgeschlagen - Auto fährt noch!");
    }
  }
}

void handleThrottle() {
  if (engine_on) {
    gas_pressed = true;
    last_gas_command = millis();
    int max_rpm_for_gear = 2000 + gear * 1000;
    target_rpm = min(7000, max_rpm_for_gear);
    Serial.println("> GAS! target_rpm=" + String(target_rpm));
  }
}

void handleBrake() {
  brake_pressed = true; gas_pressed = false;
  throttle = max(0, throttle - 25);
  target_rpm = 850; speed = max(0, speed - 8);
  Serial.println(">>> BREMSE! Throttle: " + String(throttle) + "% | Speed: " + String(speed));
  digitalWrite(LED_RECEIVER, HIGH);
  delay(20);
  digitalWrite(LED_RECEIVER, LOW);
}

void shiftUp() {
  if (!engine_on) { Serial.println(">>> Schalten fehlgeschlagen - Motor aus!"); return; }
  if (gear >= 5)   { Serial.println(">>> Bereits höchster Gang!"); return; }
  if (rpm < 1500)  { Serial.println(">>> RPM zu niedrig - Min 1500!"); return; }
  int old = gear; gear++; rpm = max(850, rpm - 400); target_rpm = max(850, target_rpm - 400);
  Serial.println(">>> HOCHGESCHALTET! " + String(old) + " -> " + String(gear) + " | RPM: " + String(rpm));
  digitalWrite(LED_SENDER, HIGH);
  delay(20);
  digitalWrite(LED_SENDER, LOW);
}

void shiftDown() {
  if (!engine_on) { Serial.println(">>> Schalten fehlgeschlagen - Motor aus!"); return; }
  if (gear <= 1)   { Serial.println(">>> Bereits niedrigster Gang!"); return; }
  int old = gear; gear--; int new_r = rpm + 500;
  if (new_r > 6000) { Serial.println(">>> Runterschalten würde überdrehen!"); gear = old; return; }
  rpm = new_r; target_rpm = min(target_rpm + 500, 7000);
  Serial.println(">>> RUNTERGESCHALTET! " + String(old) + " -> " + String(gear) + " | RPM: " + String(rpm));
  digitalWrite(LED_SENDER, HIGH);
  delay(20);
  digitalWrite(LED_SENDER, LOW);
}

void updateRPM() {
  if (!engine_on) { rpm = target_rpm = 0; return; }
  if (gas_pressed && rpm < target_rpm) {
    rpm += 80;  // Beschleunigung
  } else {
    // Leerlauf
    target_rpm = 850;
    if (rpm > target_rpm) rpm -= 30;
    else if (rpm < target_rpm) rpm += 20;
  }
  rpm = constrain(rpm, 0, 7000);
  if (rpm > 1000) speed = constrain((rpm - 850)/(20 + gear*5), 0, 200);
  else          speed = max(0, speed - 1);
  if (!gas_pressed) throttle = max(0, throttle - 5);
}

void sendStatus() {
  Serial.println("ENGINE_RUNNING:" + String(engine_on ? "1":"0"));
  Serial.println("RPM:" + String(rpm));
  Serial.println("SPEED:" + String(speed));
  Serial.println("GEAR:" + String(gear));
  Serial.println("THROTTLE:" + String(throttle));
  String rs="OK"; if(rpm>6500) rs="REDLINE"; else if(rpm>5000) rs="HIGH";
  else if(gear<5&&rpm>(2000+gear*800)) rs="SHIFT_UP";
  Serial.println("RPM_STATUS:" + rs);
  Serial.println();
}
