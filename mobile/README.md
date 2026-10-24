# Flutter driver app
```bash
cd mobile
flutter create . --platforms=android,ios    # generates android/ ios/ runner folders (keeps lib/ and pubspec.yaml)
flutter pub get
flutter run --dart-define=API=http://<your-LAN-IP>:8000
```
Screens: login/register → map of nearby chargers (OpenStreetMap, free) → book → start/stop session with live kWh → pay.
Android: add `<uses-permission android:name="android.permission.INTERNET"/>` and allow cleartext HTTP for dev.
Next: `geolocator` for GPS, Razorpay Checkout SDK, FCM push notifications, Firebase Auth / DigiLocker KYC.
