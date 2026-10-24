import 'dart:async';
import 'package:flutter/material.dart';
import '../api.dart';

/// Start/stop charging with a live kWh counter (polls the API every 3 s).
class SessionScreen extends StatefulWidget {
  final Map<String, dynamic> booking;
  const SessionScreen({super.key, required this.booking});
  @override
  State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen> {
  Map<String, dynamic>? s;
  Timer? timer;
  String msg = '';

  Future<void> run(Future<Map<String, dynamic>> Function() f) async {
    try {
      final r = await f();
      setState(() { s = r; msg = ''; });
    } catch (e) {
      setState(() => msg = '$e');
    }
  }

  void start() async {
    await run(() => Api.startSession(widget.booking['id']));
    timer?.cancel();
    timer = Timer.periodic(const Duration(seconds: 3), (_) {
      if (s != null && s!['active'] == true) run(() => Api.session(s!['id']));
    });
  }

  @override
  void dispose() { timer?.cancel(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final active = s?['active'] == true, done = s != null && !active;
    return Scaffold(
      appBar: AppBar(title: Text('Booking #${widget.booking['id']}')),
      body: Center(
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text('${(s?['kwh'] ?? 0).toStringAsFixed(3)} kWh', style: Theme.of(context).textTheme.displayMedium),
          if (s?['power_w'] != null) Text('${s!['power_w']} W'),
          Text('Total so far: ₹${s?['total'] ?? widget.booking['total_price']}'),
          const SizedBox(height: 16),
          if (s == null) FilledButton(onPressed: start, child: const Text('Start charging')),
          if (active) FilledButton(onPressed: () => run(() => Api.stopSession(s!['id'])), child: const Text('Stop & bill')),
          if (done) FilledButton(
              onPressed: () async {
                try { await Api.pay(widget.booking['id']); setState(() => msg = 'Paid ✔'); }
                catch (e) { setState(() => msg = '$e'); }
              },
              child: const Text('Pay (Razorpay test)')),
          if (msg.isNotEmpty) Padding(padding: const EdgeInsets.all(12), child: Text(msg)),
        ]),
      ),
    );
  }
}
