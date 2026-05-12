import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../main.dart';
import '../models/machine.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _defaultUser;
  late TextEditingController _tunnelWait;
  late String _theme;

  @override
  void initState() {
    super.initState();
    final s = context.read<AppState>().settings;
    _defaultUser = TextEditingController(text: s.defaultSshUser);
    _tunnelWait = TextEditingController(text: s.tunnelWaitMs.toString());
    _theme = s.theme;
  }

  @override
  void dispose() {
    _defaultUser.dispose();
    _tunnelWait.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final app = context.read<AppState>();
    final wait = int.tryParse(_tunnelWait.text) ?? 1500;
    await app.saveSettings(Settings(
      tunnelWaitMs: wait.clamp(500, 10000),
      defaultSshUser: _defaultUser.text.trim(),
      theme: _theme,
    ));
    if (mounted) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextFormField(
            controller: _defaultUser,
            decoration: const InputDecoration(
              labelText: 'Default SSH User',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _tunnelWait,
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            decoration: const InputDecoration(
              labelText: 'Tunnel Wait (ms)',
              helperText: 'Delay after SSH connects before opening VNC (500–10000 ms)',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 24),
          Text('Theme', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'light', label: Text('Light'), icon: Icon(Icons.light_mode)),
              ButtonSegment(value: 'dark', label: Text('Dark'), icon: Icon(Icons.dark_mode)),
            ],
            selected: {_theme},
            onSelectionChanged: (s) => setState(() => _theme = s.first),
          ),
          const SizedBox(height: 32),
          FilledButton(
            onPressed: _save,
            child: const Text('Save Settings'),
          ),
        ],
      ),
    );
  }
}
