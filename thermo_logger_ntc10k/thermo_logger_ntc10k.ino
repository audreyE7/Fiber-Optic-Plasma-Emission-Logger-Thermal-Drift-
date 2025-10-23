// arduino/thermo_logger_ntc10k/thermo_logger_ntc10k.ino
// NTC to A0 with 10k series to 5V; junction to A0; other end to GND.
const float R_FIXED = 10000.0;    // 10k
const float BETA    = 3950.0;     // typical
const float T0K     = 298.15;     // 25°C in Kelvin
void setup(){ Serial.begin(115200); }
void loop(){
  int raw = analogRead(A0);
  float v = raw * (5.0/1023.0);
  float r_ntc = (v>0.0001) ? (R_FIXED * (5.0 - v) / v) : 1e9;
  float invT = (1.0/T0K) + (1.0/BETA)*log(r_ntc/10000.0);
  float tempC = (1.0/invT) - 273.15;
  Serial.print("T,"); Serial.println(tempC, 2);
  delay(200);
}
