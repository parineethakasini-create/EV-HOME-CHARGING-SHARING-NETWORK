// ChargeShare ESP32 meter: relay control + PZEM-004T v3 metering + signed MQTT telemetry.
// Libraries: PubSubClient, PZEM004Tv30 (mandulaj). Board: ESP32 Dev Module.
#include <WiFi.h>
#include <PubSubClient.h>
#include <PZEM004Tv30.h>
#include <time.h>
#include "mbedtls/md.h"
#include "config.h"

PZEM004Tv30 pzem(Serial2, 16, 17);       // PZEM TX->GPIO16, RX->GPIO17
WiFiClient net;
PubSubClient mqtt(net);

String topicTelemetry = String("chargeshare/") + DEVICE_ID + "/telemetry";
String topicCmd       = String("chargeshare/") + DEVICE_ID + "/cmd";

bool relayOn = false;
int overCount = 0;
unsigned long lastSend = 0;

// Offline buffer: keep recent readings while Wi-Fi/MQTT is down, flush on reconnect.
const int BUF_N = 20;
String buf[BUF_N];
int bufCount = 0;

void setRelay(bool on) {
  relayOn = on;
  digitalWrite(RELAY_PIN, (on == (bool)RELAY_ACTIVE_HIGH) ? HIGH : LOW);
}

String hmacHex(const String &msg) {
  unsigned char out[32];
  mbedtls_md_context_t ctx;
  mbedtls_md_init(&ctx);
  mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(MBEDTLS_MD_SHA256), 1);
  mbedtls_md_hmac_starts(&ctx, (const unsigned char *)DEVICE_SECRET, strlen(DEVICE_SECRET));
  mbedtls_md_hmac_update(&ctx, (const unsigned char *)msg.c_str(), msg.length());
  mbedtls_md_hmac_finish(&ctx, out);
  mbedtls_md_free(&ctx);
  String hex;
  char b[3];
  for (int i = 0; i < 32; i++) { snprintf(b, 3, "%02x", out[i]); hex += b; }
  return hex;
}

void onMessage(char *topic, byte *payload, unsigned int len) {
  String s;
  for (unsigned int i = 0; i < len; i++) s += (char)payload[i];
  if (s.indexOf("\"on\"") >= 0) setRelay(true);
  if (s.indexOf("\"off\"") >= 0) setRelay(false);
}

void connectWifi() {
  if (WiFi.status() == WL_CONNECTED) return;
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  for (int i = 0; i < 20 && WiFi.status() != WL_CONNECTED; i++) delay(500);
}

void connectMqtt() {
  if (WiFi.status() != WL_CONNECTED || mqtt.connected()) return;
  if (mqtt.connect(DEVICE_ID)) {
    mqtt.subscribe(topicCmd.c_str(), 1);          // retained command restores last state
    while (bufCount > 0) {                        // flush offline buffer (oldest first)
      mqtt.publish(topicTelemetry.c_str(), buf[0].c_str());
      for (int i = 1; i < bufCount; i++) buf[i - 1] = buf[i];
      bufCount--;
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  setRelay(false);                                // fail-safe: off at boot
  connectWifi();
  configTime(0, 0, "pool.ntp.org");               // UTC epoch for signed timestamps
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMessage);
}

void loop() {
  connectWifi();
  connectMqtt();
  mqtt.loop();

  if (millis() - lastSend < 5000) return;
  lastSend = millis();

  time_t ts = time(nullptr);
  if (ts < 1700000000) return;                    // wait for NTP

  float kwh = pzem.energy(), p = pzem.power(), v = pzem.voltage(), a = pzem.current();
  if (isnan(kwh) || isnan(p)) return;             // meter not responding

  // software over-power cut-off (3 consecutive samples)
  overCount = (p > MAX_WATTS) ? overCount + 1 : 0;
  if (overCount >= 3) setRelay(false);

  char sigMsg[96];
  snprintf(sigMsg, sizeof(sigMsg), "%s|%lu|%.3f|%.1f", DEVICE_ID, (unsigned long)ts, kwh, p);
  char json[256];
  snprintf(json, sizeof(json),
           "{\"device_id\":\"%s\",\"ts\":%lu,\"kwh_total\":%.3f,\"power_w\":%.1f,\"voltage\":%.1f,\"current\":%.2f,\"sig\":\"%s\"}",
           DEVICE_ID, (unsigned long)ts, kwh, p, v, a, hmacHex(String(sigMsg)).c_str());

  if (mqtt.connected()) {
    mqtt.publish(topicTelemetry.c_str(), json);
  } else if (bufCount < BUF_N) {
    buf[bufCount++] = String(json);
  }
}
