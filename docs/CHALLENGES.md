# Key challenges and solutions

| Challenge | Solution | Status |
|---|---|---|
| Electrical safety | Mandatory ELCB/MCB, certified relay, host checklist; firmware over-power cut-off, relay OFF at boot | firmware ✔, checklist: docs |
| Trust between strangers | KYC, ratings, insurance or deposit | ratings ✔, KYC/deposit roadmap |
| Accurate billing | Calibrated meter, HMAC-signed readings, replay protection, anomaly flags | ✔ |
| Parking access | Gated-community access codes, visitor-pass integration | roadmap |
| Unreliable internet | Device-side offline buffer; retained MQTT commands; sync on reconnect | ✔ (20 readings) |
| Grid load | Load limits (`power_kw`, `MAX_WATTS`), scheduled charging, off-peak pricing | pricing ✔, scheduling roadmap |

## Host safety checklist (show in host onboarding)
- [ ] Dedicated circuit with correctly rated MCB and 30 mA ELCB/RCCB
- [ ] Proper earthing verified
- [ ] Weatherproof (IP-rated) socket/enclosure
- [ ] Certified relay/contactor rated for the load (not a hobby relay for >10 A)
- [ ] Wiring done by a qualified electrician
