// arduino/thermo_logger_tmp36/thermo_logger_tmp36.ino
// TMP36 on A0, Serial @ 115200
void setup() { Serial.begin(115200); }
void loop() {
  int raw = analogRead(A0);                 // 0..1023
  float v = raw * (5.0 / 1023.0);           // V
  float tempC = (v - 0.5) * 100.0;          // °C
  Serial.print("T,"); Serial.println(tempC, 2);
  delay(200); // 5 Hz
}
