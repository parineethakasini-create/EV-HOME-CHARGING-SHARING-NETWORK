import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../api.dart';
import 'session_screen.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});
  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final center = const LatLng(17.385, 78.4867); // TODO: use geolocator for real GPS
  List<dynamic> chargers = [];
  String? connector;

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    final r = await Api.search(center.latitude, center.longitude, connector: connector);
    if (mounted) setState(() => chargers = r);
  }

  void open(Map c) => showModalBottomSheet(
        context: context,
        builder: (_) => Padding(
          padding: const EdgeInsets.all(16),
          child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(c['title'], style: Theme.of(context).textTheme.titleLarge),
            Text('${c['connector']} · ${c['power_kw']} kW · ₹${c['price_per_kwh']}/kWh + ₹${c['price_per_hour']}/hr'),
            Text(c['avg_rating'] == null ? 'No reviews yet' : '★ ${c['avg_rating']}'),
            const SizedBox(height: 12),
            FilledButton(
              child: const Text('Book next hour'),
              onPressed: () async {
                final nav = Navigator.of(context);
                final msg = ScaffoldMessenger.of(context);
                try {
                  final start = DateTime.now().add(const Duration(minutes: 1));
                  final b = await Api.book(c['id'], start, start.add(const Duration(hours: 1)));
                  nav.pop();
                  nav.push(MaterialPageRoute(builder: (_) => SessionScreen(booking: b)));
                } catch (e) {
                  msg.showSnackBar(SnackBar(content: Text('$e')));
                }
              },
            ),
          ]),
        ),
      );

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Chargers near you'), actions: [
          DropdownButton<String?>(
            value: connector,
            hint: const Text('Connector'),
            items: [null, 'Type2', 'CCS2', 'J1772', 'CHAdeMO', 'NACS', 'GB/T']
                .map((e) => DropdownMenuItem(value: e, child: Text(e ?? 'All')))
                .toList(),
            onChanged: (v) {
              connector = v;
              load();
            },
          ),
        ]),
        body: FlutterMap(
          options: MapOptions(initialCenter: center, initialZoom: 12),
          children: [
            TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', userAgentPackageName: 'app.chargeshare'),
            MarkerLayer(markers: [
              for (final c in chargers)
                Marker(
                  point: LatLng(c['lat'], c['lng']),
                  width: 44,
                  height: 44,
                  child: GestureDetector(onTap: () => open(c), child: const Icon(Icons.ev_station, color: Color(0xFF0B6E4F), size: 40)),
                ),
            ]),
          ],
        ),
      );
}
