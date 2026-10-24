import 'package:flutter/material.dart';
import 'api.dart';
import 'screens/map_screen.dart';

void main() => runApp(const ChargeShareApp());

class ChargeShareApp extends StatelessWidget {
  const ChargeShareApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'ChargeShare',
        theme: ThemeData(colorSchemeSeed: const Color(0xFF0B6E4F), useMaterial3: true),
        home: const LoginScreen(),
      );
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final email = TextEditingController(), name = TextEditingController(), pw = TextEditingController();
  bool register = false;
  String err = '';

  Future<void> submit() async {
    try {
      if (register) await Api.register(email.text, name.text, pw.text, 'guest');
      await Api.login(email.text, pw.text);
      if (!mounted) return;
      Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const MapScreen()));
    } catch (e) {
      setState(() => err = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('⚡ ChargeShare')),
        body: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(children: [
            TextField(controller: email, decoration: const InputDecoration(labelText: 'Email')),
            if (register) TextField(controller: name, decoration: const InputDecoration(labelText: 'Name')),
            TextField(controller: pw, obscureText: true, decoration: const InputDecoration(labelText: 'Password (8+ chars)')),
            const SizedBox(height: 12),
            if (err.isNotEmpty) Text(err, style: const TextStyle(color: Colors.red)),
            FilledButton(onPressed: submit, child: Text(register ? 'Sign up as driver' : 'Log in')),
            TextButton(
                onPressed: () => setState(() => register = !register),
                child: Text(register ? 'Have an account? Log in' : 'New here? Register')),
          ]),
        ),
      );
}
