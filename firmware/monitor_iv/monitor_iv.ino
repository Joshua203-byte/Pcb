/*
 * Monitor I-V de panel solar  -  ESP32 DevKitC + ADS1115 + 8 reles  (PCB v20)
 * PBL Semiconductores EE2002
 *
 * MODO_PRUEBA (abajo): 1 = prueba sin sol, con la linterna del telefono (escala sensible, sin irradiancia ni envio
 * al servidor). 0 = version real para el sol.
 *
 * Que hace:
 *   - Barrido I-V de 23 puntos (64 con BARRIDO_DENSO en modo real): cierra las cargas de a una combinacion, espera 200 ms,
 *     mide V (A0 por divisor 33k/10k) e I (A2-A3 por la derivacion R_SH1) con el ADS1115.
 *   - Mide la celda de referencia (A1, derivacion R_SH2) para la irradiancia G.
 *   - DS18B20 (temperatura del panel): ACTIVADO (USAR_DS18B20 1). Pon 0 si no lo tenes conectado.
 *   - Guarda cada barrido en la microSD (CSV) con la hora del RTC DS3231.
 *   - Habla con el dashboard (dashboard_v3.html) por WebSocket (puerto 81) o por HTTP (puerto 80),
 *     y opcionalmente envia cada barrido por HTTP POST a servidor.py (SERVER_URL).
 *
 * Librerias (Administrador de bibliotecas del Arduino IDE):
 *   "Adafruit ADS1X15", "RTClib" (Adafruit), "WebSockets" (Markus Sattler),
 *   y solo si USAR_DS18B20=1: "OneWire" y "DallasTemperature".
 * Placa: "ESP32 Dev Module".
 */

#include <Arduino.h>      // tiene que ir primero: define uint8_t, uint32_t, etc. que usa la configuracion

// ============================== CONFIGURACION ==============================
// ---- Wi-Fi. Si no conecta en 15 s crea su propia red (IP 192.168.4.1) para que puedas probar igual.
const char* WIFI_SSID = "TU_RED";
const char* WIFI_PASS = "TU_CLAVE";
const char* AP_SSID   = "MonitorIV";
const char* AP_PASS   = "12345678";          // minimo 8 caracteres
// ---- Servidor Python (opcional). Vacio = no envia. Ejemplo: "http://192.168.1.10:8000/api/barrido"
const char* SERVER_URL = "";

// ---- 1 = PRUEBA SIN SOL (luz del telefono): lee corrientes de miliamperios con mas sensibilidad.
//      0 = REAL (sol): escala normal, irradiancia por la celda de referencia, envio al servidor.
#define MODO_PRUEBA 0     // <- pon 1 solo si pruebas de noche con la linterna del telefono

// ---- Cantidad de puntos del barrido (solo en modo real, con sol): 1 = 64 puntos (unos 20 s), 0 = 23 puntos (unos 8 s).
//      En modo prueba (linterna) siempre son 23: con poca luz mas puntos no mejoran la curva.
#define BARRIDO_DENSO 1

// ---- Que hardware esta conectado
#define USAR_DS18B20   1      // 1 = DS18B20 conectado en J3 (necesita "OneWire" y "DallasTemperature"); 0 = no conectado
#define USAR_RTC       1      // DS3231
#define USAR_SD        1      // modulo microSD
#define USAR_CELDA_REF 1      // celda de referencia en J4 (si no hay celda, G sale vacia y el dashboard la estima)

// ---- Barrido automatico: cada cuantos segundos (0 = solo cuando lo pides en el dashboard; 600 = cada 10 min)
const uint32_t AUTO_BARRIDO_S = 0;

// ---- Pines de la PCB v20
const int PIN_SDA = 33, PIN_SCL = 32;        // I2C: ADS1115 (0x48) y RTC (0x68)
const int PIN_DQ  = 14;                      // DS18B20
const int PIN_SCK = 5, PIN_MISO = 19, PIN_MOSI = 18, PIN_CS = 17;   // microSD
const uint8_t RELE_PIN[8] = {16, 4, 21, 22, 23, 25, 26, 27};        // IN1..IN8 -> RL1..RL8
// Los modulos de 8 reles se alimentan a 5 V y se activan con LOW. Con la logica de 3.3 V del ESP32, un HIGH NO alcanza para
// apagarlos (quedan encendidos y se calientan). Solucion: apagado = pin flotante (INPUT), encendido = OUTPUT en LOW.
#define RELE_ENTRADA_FLOTANTE 1                  // 1 = lo de arriba (recomendado). 0 = nivel normal con RELE_ACTIVO_BAJO
const bool RELE_ACTIVO_BAJO = true;              // solo se usa si RELE_ENTRADA_FLOTANTE es 0

// ---- Medicion (pon aqui los valores que midas con el multimetro)
const float DIV_R1 = 33000.0f, DIV_R2 = 10000.0f;   // divisor del voltaje del panel
const float R_SHUNT     = 1.0f;     // R_SH1 en ohm (1 ohm; si usas dos de 2 ohm en paralelo tambien es 1.0)
const float R_SHUNT_REF = 1.0f;     // R_SH2 en ohm
const float ISC_CELDA_REF = 0.212f; // corriente de cortocircuito de la celda de referencia a 1000 W/m2 (A)
const float ALFA_ISC = 0.0005f;     // +0.05 %/C
const float UMBRAL_CELDA_V = 0.010f; // por debajo de 10 mV en A1 se considera que no hay celda de referencia
const uint16_t ESPERA_RELE_MS = 200;  // asentamiento tras cerrar un rele
#if MODO_PRUEBA
  #define GANANCIA_I GAIN_SIXTEEN     // +-0.256 V sobre R_SH1: 7.8 uV por cuenta (corrientes de mA)
  const uint8_t MUESTRAS = 16;        // mas promedio: la senal es chica
#else
  #define GANANCIA_I GAIN_EIGHT       // +-0.512 V sobre R_SH1: hasta 0.5 A con 1 ohm
  const uint8_t MUESTRAS = 8;
#endif

// Combinaciones de reles (bit0 = RL1 ... bit7 = RL8), de menor a mayor voltaje; 0x00 = circuito abierto.
// Elegidas con los valores nominales de las cargas (2.2, 4.7, 10, 22, 47, 100, 220, 470 ohm) y repartidas a lo largo de la curva I-V.
#if MODO_PRUEBA || !BARRIDO_DENSO
// 23 puntos
const uint8_t MASCARAS[] = {0x01,0x3C,0xA4,0x78,0xE8,0xC8,0x08,0xF0,0x70,0xB0,0x30,0xD0,
                            0x50,0x90,0x10,0xE0,0x60,0xA0,0x20,0xC0,0x40,0x80,0x00};
#else
// 64 puntos
const uint8_t MASCARAS[] = {0xFF,0xFE,0x9A,0x02,0xDC,0x5C,0x9C,0x1C,0xEC,0x6C,0xAC,0x2C,0xCC,0x4C,0x8C,0x0C,
                            0xF4,0x74,0xB4,0x34,0xD4,0x54,0x94,0x14,0xE4,0x64,0xA4,0x24,0xC4,0x44,0x84,0x04,
                            0xF8,0x78,0xB8,0x38,0xD8,0x58,0x98,0x18,0xE8,0x68,0xA8,0x28,0xC8,0x48,0x88,0x08,
                            0xF0,0x70,0xB0,0x30,0xD0,0x50,0x90,0x10,0xE0,0x60,0xA0,0x20,0xC0,0x40,0x80,0x00};
#endif
const uint8_t N_PUNTOS = sizeof(MASCARAS);
// ============================================================================

#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <ESPmDNS.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#if USAR_RTC
#include <RTClib.h>
#endif
#if USAR_SD
#include <SPI.h>
#include <SD.h>
#endif
#if USAR_DS18B20
#include <OneWire.h>
#include <DallasTemperature.h>
OneWire oneWire(PIN_DQ);
DallasTemperature sensorT(&oneWire);
#endif

#define FW_VERSION "1.0"

Adafruit_ADS1115 ads;
WebServer web(80);
WebSocketsServer ws(81);
#if USAR_RTC
RTC_DS3231 rtc;
#endif

bool adsOk = false, rtcOk = false, sdOk = false;
uint32_t epochBase = 0, milisBase = 0;      // reloj de respaldo si no hay RTC

struct Punto { uint8_t mascara; float v, i; };
Punto puntos[N_PUNTOS];
uint8_t nPuntos = 0, paso = 0;
bool barriendo = false, barridoListo = false;
uint32_t tListo = 0, tUltimoBarrido = 0, tTelemetria = 0, tReintento = 0;
uint8_t pollIdx = 0;
float tempBarrido = NAN, gBarrido = NAN, tempUltima = NAN;
uint32_t idBarrido = 0, tsBarrido = 0;
bool pendienteEnvio = false;
char buf[320];

// ------------------------------------------------------------------ utilidades
static void fnum(char* out, size_t n, float x, int d) {
  if (isnan(x) || isinf(x)) snprintf(out, n, "null"); else snprintf(out, n, "%.*f", d, x);
}

uint32_t epochActual() {
#if USAR_RTC
  if (rtcOk) return rtc.now().unixtime();
#endif
  if (epochBase) return epochBase + (millis() - milisBase) / 1000;
  return 0;
}

void fijarHora(uint32_t epoch) {
  epochBase = epoch; milisBase = millis();
#if USAR_RTC
  if (rtcOk) rtc.adjust(DateTime(epoch));
#endif
}

// ---------------------------------------------------------------------- reles
void releSet(uint8_t k, bool on) {
#if RELE_ENTRADA_FLOTANTE
  if (on) { digitalWrite(RELE_PIN[k], LOW); pinMode(RELE_PIN[k], OUTPUT); }
  else    { pinMode(RELE_PIN[k], INPUT); }
#else
  digitalWrite(RELE_PIN[k], on ? (RELE_ACTIVO_BAJO ? LOW : HIGH) : (RELE_ACTIVO_BAJO ? HIGH : LOW));
#endif
}

void aplicarMascara(uint8_t m) {
  for (uint8_t k = 0; k < 8; k++) releSet(k, (m >> k) & 1);
}

void relesInicio() {
#if !RELE_ENTRADA_FLOTANTE
  for (uint8_t k = 0; k < 8; k++) { digitalWrite(RELE_PIN[k], RELE_ACTIVO_BAJO ? HIGH : LOW); pinMode(RELE_PIN[k], OUTPUT); }
#else
  aplicarMascara(0);                     // todos apagados desde el primer instante
#endif
}

// ------------------------------------------------------------------ mediciones
float leerVoltajePanel() {            // A0, escala +-4.096 V
  ads.setGain(GAIN_ONE);
  float s = 0;
  for (uint8_t n = 0; n < MUESTRAS; n++) s += ads.computeVolts(ads.readADC_SingleEnded(0));
  return (s / MUESTRAS) * (DIV_R1 + DIV_R2) / DIV_R2;
}

float offsetI = 0;                    // voltaje de offset del shunt con los reles abiertos (autocero)

float shuntCrudo() {                  // A2-A3 sobre R_SH1, en volts
  ads.setGain(GANANCIA_I);
  float s = 0;
  for (uint8_t n = 0; n < MUESTRAS; n++) s += ads.computeVolts(ads.readADC_Differential_2_3());
  return s / MUESTRAS;
}

void autoCero() { offsetI = shuntCrudo(); }   // llamar solo con todos los reles abiertos

float leerCorrientePanel(float v) {   // corriente del panel (shunt sin offset + corriente del divisor)
  float i = (shuntCrudo() - offsetI) / R_SHUNT;
  if (i < 0) i = 0;
  return i + v / (DIV_R1 + DIV_R2);
}

float leerTemperatura() {
#if USAR_DS18B20
  sensorT.requestTemperatures();
  float t = sensorT.getTempCByIndex(0);
  if (t > -100 && t < 125) { tempUltima = t; return t; }
#endif
  return NAN;
}

float leerIrradiancia(float temp) {   // A1 sobre R_SH2: corriente de la celda de referencia
#if USAR_CELDA_REF && !MODO_PRUEBA
  ads.setGain(GAIN_EIGHT);
  float s = 0;
  for (uint8_t n = 0; n < MUESTRAS; n++) s += ads.computeVolts(ads.readADC_SingleEnded(1));
  float vref = s / MUESTRAS;
  if (vref < UMBRAL_CELDA_V) return NAN;   // celda no conectada (A1 queda a GND por R_SH2)
  float T = isnan(temp) ? 25.0f : temp;
  float isc = (vref / R_SHUNT_REF);
  return 1000.0f * isc / (ISC_CELDA_REF * (1.0f + ALFA_ISC * (T - 25.0f)));
#else
  return NAN;
#endif
}

// ------------------------------------------------------------------- mensajes
void enviarHello(int8_t num) {
  char t[16]; fnum(t, sizeof t, tempUltima, 1);
  snprintf(buf, sizeof buf, "{\"type\":\"hello\",\"firmware\":\"%s\",\"model\":\"ESP32 + ADS1115 (PCB v20)\",\"temperature\":%s,"
           "\"ads\":%s,\"rtc\":%s,\"sd\":%s,\"test\":%s}", FW_VERSION, t, adsOk ? "true" : "false", rtcOk ? "true" : "false", sdOk ? "true" : "false",
           MODO_PRUEBA ? "true" : "false");
  if (num >= 0) ws.sendTXT(num, buf); else ws.broadcastTXT(buf);
}

void enviarError(const char* msg) {
  snprintf(buf, sizeof buf, "{\"type\":\"error\",\"message\":\"%s\"}", msg);
  ws.broadcastTXT(buf);
}

// ----------------------------------------------------------------- microSD / POST
void guardarSD() {
#if USAR_SD
  if (!sdOk) return;
  bool nuevo = !SD.exists("/barridos.csv");
  File f = SD.open("/barridos.csv", FILE_APPEND);
  if (!f) return;
  if (nuevo) f.println("epoch,barrido,paso,mascara,v_V,i_A,p_W,temperatura_C,irradiancia_Wm2");
  for (uint8_t k = 0; k < nPuntos; k++) {
    char t[16], g[16]; fnum(t, sizeof t, tempBarrido, 1); fnum(g, sizeof g, gBarrido, 0);
    f.printf("%lu,%lu,%u,0x%02X,%.4f,%.5f,%.5f,%s,%s\n", (unsigned long)tsBarrido, (unsigned long)idBarrido, k + 1,
             puntos[k].mascara, puntos[k].v, puntos[k].i, puntos[k].v * puntos[k].i,
             isnan(tempBarrido) ? "" : t, isnan(gBarrido) ? "" : g);
  }
  f.close();
#endif
}

bool enviarAlServidor() {
  if (strlen(SERVER_URL) == 0) return true;
  if (WiFi.status() != WL_CONNECTED) return false;
  char t[16], g[16]; fnum(t, sizeof t, tempBarrido, 1); fnum(g, sizeof g, gBarrido, 1);
  String body;
  body.reserve(3200);
  body += "{\"device\":\"monitor-iv\",\"id\":"; body += idBarrido;
  body += ",\"ts\":"; body += tsBarrido;
  body += ",\"temperature\":"; body += t;
  body += ",\"irradiance\":"; body += g;
  body += ",\"points\":[";
  for (uint8_t k = 0; k < nPuntos; k++) {
    char p[64]; snprintf(p, sizeof p, "%s[%.4f,%.5f]", k ? "," : "", puntos[k].v, puntos[k].i);
    body += p;
  }
  body += "]}";
  HTTPClient h;
  h.begin(SERVER_URL);
  h.addHeader("Content-Type", "application/json");
  h.setTimeout(4000);
  int code = h.POST(body);
  h.end();
  return code == 200;
}

// ---------------------------------------------------------------------- barrido
void iniciarBarrido() {
  if (barriendo) return;
  if (!adsOk) { enviarError("ADS1115 no responde (revisa SDA=33, SCL=32 y la direccion 0x48)."); return; }
  barriendo = true; barridoListo = false; paso = 0; nPuntos = 0; pollIdx = 0;
  idBarrido++; tsBarrido = epochActual();
  aplicarMascara(0); autoCero();       // offset del shunt con todo abierto
  tempBarrido = leerTemperatura();
  snprintf(buf, sizeof buf, "{\"type\":\"sweep_start\",\"points\":%u}", N_PUNTOS);
  ws.broadcastTXT(buf);
  aplicarMascara(MASCARAS[0]);
  tListo = millis() + ESPERA_RELE_MS;
}

void abortarBarrido() {
  aplicarMascara(0);
  barriendo = false; barridoListo = false;
}

void finalizarBarrido() {
  aplicarMascara(0);
  barriendo = false; barridoListo = true;
  float t2 = leerTemperatura();
  if (!isnan(tempBarrido) && !isnan(t2)) tempBarrido = (tempBarrido + t2) / 2; else if (!isnan(t2)) tempBarrido = t2;
  gBarrido = leerIrradiancia(tempBarrido);
  char t[16], g[16]; fnum(t, sizeof t, tempBarrido, 1); fnum(g, sizeof g, gBarrido, 1);
  snprintf(buf, sizeof buf, "{\"type\":\"sweep_end\",\"temperature\":%s,\"irradiance\":%s,\"ts\":%lu,\"id\":%lu}",
           t, g, (unsigned long)tsBarrido, (unsigned long)idBarrido);
  ws.broadcastTXT(buf);
  guardarSD();
  pendienteEnvio = strlen(SERVER_URL) > 0 && !MODO_PRUEBA;   // en prueba no se ensucia el historial del servidor
  tReintento = 0;
  tUltimoBarrido = millis();
}

void pasoBarrido() {
  if (!barriendo || (int32_t)(millis() - tListo) < 0) return;
  Punto& p = puntos[nPuntos];
  p.mascara = MASCARAS[paso];
  p.v = leerVoltajePanel();
  p.i = leerCorrientePanel(p.v);
  nPuntos++;
  char v[16], i[16]; fnum(v, sizeof v, p.v, 4); fnum(i, sizeof i, p.i, 5);
  snprintf(buf, sizeof buf, "{\"type\":\"sweep_point\",\"step\":%u,\"mask\":%u,\"v\":%s,\"i\":%s}", nPuntos, p.mascara, v, i);
  ws.broadcastTXT(buf);
  paso++;
  if (paso >= N_PUNTOS) finalizarBarrido();
  else { aplicarMascara(MASCARAS[paso]); tListo = millis() + ESPERA_RELE_MS; }
}

uint32_t tTemp = 0;
void refrescarTemperatura() {
#if USAR_DS18B20
  if (barriendo || millis() - tTemp < 10000) return;
  tTemp = millis();
  leerTemperatura();
#endif
}

void telemetria() {
  if (barriendo || !adsOk || ws.connectedClients() == 0 || millis() - tTelemetria < 2000) return;
  tTelemetria = millis();
  autoCero();                          // con los reles abiertos la corriente es 0: se re-calibra el offset
  float v = leerVoltajePanel();
  float i = leerCorrientePanel(v);
  char sv[16], si[16], st[16], sg[16];
  fnum(sv, sizeof sv, v, 3); fnum(si, sizeof si, i, 5); fnum(st, sizeof st, tempUltima, 1); fnum(sg, sizeof sg, leerIrradiancia(tempUltima), 0);
  snprintf(buf, sizeof buf, "{\"type\":\"telemetry\",\"v\":%s,\"i\":%s,\"temperature\":%s,\"irradiance\":%s}", sv, si, st, sg);
  ws.broadcastTXT(buf);
}

// ------------------------------------------------------------- WebSocket (puerto 81)
void wsEvento(uint8_t num, WStype_t type, uint8_t* payload, size_t len) {
  if (type == WStype_CONNECTED) { enviarHello(num); return; }
  if (type != WStype_TEXT) return;
  const char* m = (const char*)payload;
  if (strstr(m, "\"START\"")) iniciarBarrido();
  else if (strstr(m, "\"ABORT\"")) abortarBarrido();
  else if (strstr(m, "\"TIME\"")) {
    const char* e = strstr(m, "\"epoch\"");
    if (e && (e = strchr(e, ':'))) { uint32_t ep = strtoul(e + 1, nullptr, 10); if (ep > 1600000000UL) fijarHora(ep); }
  }
}

// ---------------------------------------------------------- HTTP (puerto 80, polling)
void cors() {
  web.sendHeader("Access-Control-Allow-Origin", "*");
  web.sendHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  web.sendHeader("Access-Control-Allow-Headers", "*");
}
void responder(int code, const char* json) { cors(); web.send(code, "application/json", json); }

void httpInicio() {
  snprintf(buf, sizeof buf, "<meta charset=utf-8><h2>Monitor I-V (ESP32)</h2><p>Abre <b>dashboard_v3.html</b> en tu computadora y conectate a esta IP: <b>%s</b></p>",
           (WiFi.getMode() == WIFI_AP ? WiFi.softAPIP() : WiFi.localIP()).toString().c_str());
  cors(); web.send(200, "text/html", buf);
}
void httpStart() {
  if (web.method() == HTTP_OPTIONS) { cors(); web.send(204); return; }
  iniciarBarrido();
  responder(200, "{\"ok\":true}");
}
void httpPunto() {
  if (web.method() == HTTP_OPTIONS) { cors(); web.send(204); return; }
  char t[16], g[16]; fnum(t, sizeof t, tempBarrido, 1); fnum(g, sizeof g, gBarrido, 1);
  if (pollIdx < nPuntos) {
    char v[16], i[16]; fnum(v, sizeof v, puntos[pollIdx].v, 4); fnum(i, sizeof i, puntos[pollIdx].i, 5);
    snprintf(buf, sizeof buf, "{\"v\":%s,\"i\":%s}", v, i);
    pollIdx++;
  } else if (barridoListo) {
    snprintf(buf, sizeof buf, "{\"done\":true,\"temperature\":%s,\"irradiance\":%s}", t, g);
  } else strcpy(buf, "{}");
  responder(200, buf);
}
void httpEstado() {
  snprintf(buf, sizeof buf, "{\"firmware\":\"%s\",\"ads\":%s,\"rtc\":%s,\"sd\":%s,\"barriendo\":%s}", FW_VERSION,
           adsOk ? "true" : "false", rtcOk ? "true" : "false", sdOk ? "true" : "false", barriendo ? "true" : "false");
  responder(200, buf);
}

// -------------------------------------------------------------------------- setup
void conectarWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.printf("Conectando a %s", WIFI_SSID);
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 15000) { delay(300); Serial.print('.'); }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\nWi-Fi OK. IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    WiFi.disconnect(true);
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    Serial.printf("\nSin Wi-Fi: red propia \"%s\" (clave %s). IP: %s\n", AP_SSID, AP_PASS, WiFi.softAPIP().toString().c_str());
  }
  if (MDNS.begin("monitoriv")) Serial.println("Tambien en http://monitoriv.local");
}

void setup() {
  Serial.begin(115200);
  relesInicio();
  Wire.begin(PIN_SDA, PIN_SCL);
  adsOk = ads.begin(0x48, &Wire);
  if (adsOk) ads.setDataRate(RATE_ADS1115_128SPS);
  Serial.printf("ADS1115: %s\n", adsOk ? "OK" : "NO RESPONDE");
#if USAR_RTC
  rtcOk = rtc.begin(&Wire);
  if (rtcOk && rtc.lostPower()) rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));   // el dashboard la corrige al conectarse
  Serial.printf("RTC DS3231: %s\n", rtcOk ? "OK" : "NO RESPONDE");
#endif
#if USAR_SD
  SPI.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);
  sdOk = SD.begin(PIN_CS, SPI);
  Serial.printf("microSD: %s\n", sdOk ? "OK" : "NO RESPONDE");
#endif
#if USAR_DS18B20
  sensorT.begin();
  sensorT.setResolution(10);
  leerTemperatura();
  Serial.printf("DS18B20: %s\n", isnan(tempUltima) ? "NO RESPONDE (revisa J3, R4 y el puente JP1)" : "OK");
#endif
  conectarWiFi();
  web.on("/", httpInicio);
  web.on("/sweep/start", HTTP_ANY, httpStart);
  web.on("/sweep/point", HTTP_ANY, httpPunto);
  web.on("/status", httpEstado);
  web.begin();
  ws.begin();
  ws.onEvent(wsEvento);
  Serial.println("Listo. Dashboard: WebSocket ws://<IP>:81  |  HTTP http://<IP>");
}

void loop() {
  ws.loop();
  web.handleClient();
  pasoBarrido();
  refrescarTemperatura();
  telemetria();
  if (!barriendo && AUTO_BARRIDO_S > 0 && millis() - tUltimoBarrido > AUTO_BARRIDO_S * 1000UL) { tUltimoBarrido = millis(); iniciarBarrido(); }
  if (pendienteEnvio && !barriendo && (int32_t)(millis() - tReintento) >= 0) {
    if (enviarAlServidor()) pendienteEnvio = false; else tReintento = millis() + 30000;   // reintenta cada 30 s
  }
}
