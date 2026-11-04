/*
 * PRUEBA DE LA PCB v20  -  ESP32 + ADS1115 + RTC DS3231 + microSD + 8 reles
 * Abre el Monitor Serie a 115200 baudios, con "Nueva linea" (New Line) en el desplegable.
 * Escribi una letra o numero y apreta Enter:
 *   h = ayuda        i = escanear I2C (tiene que salir 0x48 y 0x68)
 *   a = lecturas del ADS1115 (todas las entradas, una vez)
 *   l = lecturas del ADS1115 en vivo (cada 0.5 s; otra "l" para parar)
 *   t = hora del RTC (y "T" para ponerlo en la hora de compilacion)
 *   s = prueba de la microSD (escribe y lee un archivo)
 *   r = probar los 8 reles uno por uno (se oye el clic)
 *   1..8 = cambia el rele k (enciende/apaga)      0 = apaga todos los reles
 *   w = prueba de Wi-Fi (busca redes)
 *   x = hace todas las pruebas automaticas (i, a, t, s, w)
 * Librerias: "Adafruit ADS1X15", "RTClib" (Adafruit). SD, SPI y WiFi ya vienen con la placa ESP32.
 */
#include <Arduino.h>

// ----- Pines de la PCB v20 (iguales a monitor_iv.ino)
const int PIN_SDA = 33, PIN_SCL = 32;
const int PIN_SCK = 5, PIN_MISO = 19, PIN_MOSI = 18, PIN_CS = 17;
const uint8_t RELE_PIN[8] = {16, 4, 21, 22, 23, 25, 26, 27};     // IN1..IN8
const bool RELE_ACTIVO_BAJO = false;     // pone true si tu modulo se activa con LOW
const float DIV = (33000.0f + 10000.0f) / 10000.0f;              // divisor R1/R2 del voltaje del panel
const float R_SHUNT = 1.0f, R_SHUNT_REF = 1.0f;                  // R_SH1 y R_SH2 (ohm)

#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <RTClib.h>
#include <SPI.h>
#include <SD.h>
#include <WiFi.h>

Adafruit_ADS1115 ads;
RTC_DS3231 rtc;
bool adsOk = false, rtcOk = false, sdOk = false, envivo = false;
bool releOn[8] = {false};
uint32_t tViva = 0;

void ponerRele(uint8_t k, bool on) {
  releOn[k] = on;
  digitalWrite(RELE_PIN[k], on ? (RELE_ACTIVO_BAJO ? LOW : HIGH) : (RELE_ACTIVO_BAJO ? HIGH : LOW));
}

void todosApagados() { for (uint8_t k = 0; k < 8; k++) ponerRele(k, false); }

void ayuda() {
  Serial.println(F("\n=== PRUEBA DE LA PCB v20 ==="));
  Serial.println(F("h ayuda | i escanear I2C | a ADS1115 | l ADS en vivo | t hora RTC (T = ajustar) | s microSD"));
  Serial.println(F("r reles uno por uno | 1..8 cambia un rele | 0 apaga todos | w Wi-Fi | x todas las pruebas\n"));
}

void escanearI2C() {
  Serial.println(F("-- Escaneo I2C (SDA=33, SCL=32) --"));
  int n = 0;
  for (byte a = 1; a < 127; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.printf("  Encontrado 0x%02X", a);
      if (a == 0x48) Serial.print(F("  <- ADS1115"));
      if (a == 0x68) Serial.print(F("  <- RTC DS3231"));
      Serial.println();
      n++;
    }
  }
  if (!n) Serial.println(F("  NADA: revisa alimentacion, SDA/SCL, orientacion de los modulos y limpia el flux con alcohol."));
}

void leerADS() {
  if (!adsOk) { Serial.println(F("ADS1115: no responde (usa 'i')")); return; }
  ads.setGain(GAIN_ONE);                                     // +-4.096 V
  float a0 = ads.computeVolts(ads.readADC_SingleEnded(0));
  float a2 = ads.computeVolts(ads.readADC_SingleEnded(2));
  float a3 = ads.computeVolts(ads.readADC_SingleEnded(3));
  ads.setGain(GAIN_EIGHT);                                   // +-0.512 V
  float a1 = ads.computeVolts(ads.readADC_SingleEnded(1));
  float dif = ads.computeVolts(ads.readADC_Differential_2_3());
  Serial.printf("A0 = %.4f V  -> voltaje del panel = %.3f V (divisor 4.3:1)\n", a0, a0 * DIV);
  Serial.printf("A1 = %.4f V  -> corriente celda de referencia = %.4f A\n", a1, a1 / R_SHUNT_REF);
  Serial.printf("A2 = %.4f V (LB)   A3 = %.4f V (GND)\n", a2, a3);
  Serial.printf("A2-A3 = %.5f V  -> corriente del panel = %.5f A (%.3f mA)\n", dif, dif / R_SHUNT, dif / R_SHUNT * 1000.0f);
}

void leerRTC(bool ajustar) {
  if (!rtcOk) { Serial.println(F("RTC: no responde (usa 'i'; revisa el puente JP1 que le da 3.3 V)")); return; }
  if (ajustar) { rtc.adjust(DateTime(F(__DATE__), F(__TIME__))); Serial.println(F("RTC ajustado a la hora de compilacion.")); }
  DateTime n = rtc.now();
  Serial.printf("RTC: %04d-%02d-%02d %02d:%02d:%02d  (temperatura del chip %.1f C)%s\n", n.year(), n.month(), n.day(),
                n.hour(), n.minute(), n.second(), rtc.getTemperature(), rtc.lostPower() ? "  [PERDIO LA HORA: usa 'T']" : "");
}

void pruebaSD() {
  if (!sdOk) { Serial.println(F("microSD: no responde (tarjeta puesta? formato FAT32? modulo de 5 V?)")); return; }
  File f = SD.open("/prueba.txt", FILE_WRITE);
  if (!f) { Serial.println(F("microSD: no pude crear el archivo")); return; }
  f.println("hola PCB v20");
  f.close();
  f = SD.open("/prueba.txt");
  Serial.print(F("microSD: leido -> "));
  while (f && f.available()) Serial.write(f.read());
  if (f) f.close();
  SD.remove("/prueba.txt");
  Serial.printf("microSD OK. Tamano de la tarjeta: %llu MB\n", SD.cardSize() / (1024ULL * 1024ULL));
}

void pruebaReles() {
  Serial.println(F("-- Reles uno por uno (escucha el clic; lo ideal es mirar el LED de cada rele) --"));
  todosApagados();
  for (uint8_t k = 0; k < 8; k++) {
    Serial.printf("  RL%d (IN%d, GPIO%d) ON\n", k + 1, k + 1, RELE_PIN[k]);
    ponerRele(k, true); delay(700);
    ponerRele(k, false); delay(300);
  }
  Serial.println(F("  Listo. Si estan al reves (todos ON en reposo), cambia RELE_ACTIVO_BAJO."));
}

void pruebaWiFi() {
  Serial.println(F("-- Wi-Fi: buscando redes de 2.4 GHz --"));
  WiFi.mode(WIFI_STA);
  int n = WiFi.scanNetworks();
  if (n <= 0) { Serial.println(F("  no encontro redes")); return; }
  for (int i = 0; i < n && i < 8; i++) Serial.printf("  %s  (%d dBm)\n", WiFi.SSID(i).c_str(), WiFi.RSSI(i));
}

void todo() { escanearI2C(); leerADS(); leerRTC(false); pruebaSD(); pruebaWiFi(); }

void setup() {
  for (uint8_t k = 0; k < 8; k++) {                         // reles apagados desde el primer instante
    digitalWrite(RELE_PIN[k], RELE_ACTIVO_BAJO ? HIGH : LOW);
    pinMode(RELE_PIN[k], OUTPUT);
  }
  Serial.begin(115200);
  delay(500);
  Wire.begin(PIN_SDA, PIN_SCL);
  adsOk = ads.begin(0x48, &Wire);
  rtcOk = rtc.begin(&Wire);
  SPI.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);
  sdOk = SD.begin(PIN_CS, SPI);
  Serial.printf("\nADS1115: %s | RTC: %s | microSD: %s\n", adsOk ? "OK" : "NO RESPONDE", rtcOk ? "OK" : "NO RESPONDE", sdOk ? "OK" : "NO RESPONDE");
  ayuda();
}

void loop() {
  if (envivo && millis() - tViva > 500) { tViva = millis(); leerADS(); Serial.println(); }
  if (!Serial.available()) return;
  char c = Serial.read();
  if (c == '\n' || c == '\r' || c == ' ') return;
  switch (c) {
    case 'h': ayuda(); break;
    case 'i': escanearI2C(); break;
    case 'a': leerADS(); break;
    case 'l': envivo = !envivo; Serial.println(envivo ? F("En vivo: ON ('l' para parar)") : F("En vivo: OFF")); break;
    case 't': leerRTC(false); break;
    case 'T': leerRTC(true); break;
    case 's': pruebaSD(); break;
    case 'r': pruebaReles(); break;
    case 'w': pruebaWiFi(); break;
    case 'x': todo(); break;
    case '0': todosApagados(); Serial.println(F("Todos los reles apagados.")); break;
    default:
      if (c >= '1' && c <= '8') { uint8_t k = c - '1'; ponerRele(k, !releOn[k]); Serial.printf("RL%d %s\n", k + 1, releOn[k] ? "ON" : "OFF"); }
      else Serial.println(F("No entendi. 'h' muestra la ayuda."));
  }
}
