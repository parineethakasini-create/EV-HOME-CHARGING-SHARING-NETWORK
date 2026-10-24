import 'dart:convert';
import 'package:http/http.dart' as http;

// Android emulator -> host machine is 10.0.2.2. Use your LAN IP on a real phone.
const apiBase = String.fromEnvironment('API', defaultValue: 'http://10.0.2.2:8000');

class Api {
  static String? token;

  static Map<String, String> get _h =>
      {'Content-Type': 'application/json', if (token != null) 'Authorization': 'Bearer $token'};

  static dynamic _check(http.Response r) {
    final body = r.body.isEmpty ? null : jsonDecode(r.body);
    if (r.statusCode >= 400) throw Exception(body is Map ? body['detail'] ?? r.reasonPhrase : r.reasonPhrase);
    return body;
  }

  static Future<void> login(String email, String pw) async {
    final r = await http.post(Uri.parse('$apiBase/auth/login'), body: {'username': email, 'password': pw});
    token = _check(r)['access_token'];
  }

  static Future<void> register(String email, String name, String pw, String role) async =>
      _check(await http.post(Uri.parse('$apiBase/auth/register'),
          headers: _h, body: jsonEncode({'email': email, 'name': name, 'password': pw, 'role': role})));

  static Future<List<dynamic>> search(double lat, double lng, {String? connector}) async =>
      _check(await http.get(Uri.parse('$apiBase/chargers').replace(queryParameters: {
        'lat': '$lat', 'lng': '$lng', 'radius_km': '25', if (connector != null) 'connector': connector
      })));

  static Future<Map<String, dynamic>> book(int chargerId, DateTime start, DateTime end) async =>
      _check(await http.post(Uri.parse('$apiBase/bookings'),
          headers: _h,
          body: jsonEncode({
            'charger_id': chargerId,
            'start_time': start.toUtc().toIso8601String(),
            'end_time': end.toUtc().toIso8601String()
          })));

  static Future<Map<String, dynamic>> startSession(int bookingId) async =>
      _check(await http.post(Uri.parse('$apiBase/sessions/start'), headers: _h, body: jsonEncode({'booking_id': bookingId})));

  static Future<Map<String, dynamic>> session(int id) async =>
      _check(await http.get(Uri.parse('$apiBase/sessions/$id'), headers: _h));

  static Future<Map<String, dynamic>> stopSession(int id) async =>
      _check(await http.post(Uri.parse('$apiBase/sessions/$id/stop'), headers: _h));

  static Future<Map<String, dynamic>> pay(int bookingId) async =>
      _check(await http.post(Uri.parse('$apiBase/payments/booking/$bookingId/pay'), headers: _h));
}
