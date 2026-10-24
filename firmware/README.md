# ESP32 meter prototype

| Part | Connection |
|---|---|
| ESP32 GPIO26 | Relay module IN (10 A+ rated, optoisolated) |
| ESP32 GPIO16 / GPIO17 | PZEM-004T v3 TX / RX (use 5 V supply for PZEM, level-shift if needed) |
| Mains | Live → PZEM CT/inline → relay COM/NO → socket. **Fit an MCB + ELCB. Have mains wiring done by a qualified electrician.** |

1. Install Arduino libraries: `PubSubClient`, `PZEM004Tv30`.
2. `cp config.h.example config.h`, fill in Wi-Fi, broker, and device credentials (`GET /chargers/{id}/device`).
3. Flash `esp32_meter.ino`.

Behaviour: relay OFF at boot; obeys retained `chargeshare/<id>/cmd`; publishes HMAC-signed readings every 5 s;
buffers 20 readings offline; software cut-off above `MAX_WATTS`.
No hardware? Use `simulator/device_sim.py`.
