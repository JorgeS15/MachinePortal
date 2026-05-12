import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import 'data/machine_repository.dart';
import 'data/settings_repository.dart';
import 'models/machine.dart';
import 'screens/dashboard_screen.dart';
import 'services/ping_service.dart';
import 'services/ssh_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AppState()),
      ],
      child: const MachinePortalApp(),
    ),
  );
}

class MachinePortalApp extends StatelessWidget {
  const MachinePortalApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, app, child) => MaterialApp(
        title: 'MachinePortal',
        debugShowCheckedModeBanner: false,
        theme: _buildTheme(app.settings.theme == 'dark'),
        home: const DashboardScreen(),
      ),
    );
  }

  ThemeData _buildTheme(bool dark) {
    // Colors from the desktop app:
    //   light: accent #72b81a (lime green)
    //   dark:  accent #7c6af7 (purple)
    final accent = dark ? const Color(0xff7c6af7) : const Color(0xff72b81a);
    final brightness = dark ? Brightness.dark : Brightness.light;

    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: ColorScheme.fromSeed(
        seedColor: accent,
        brightness: brightness,
      ),
      cardTheme: CardThemeData(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor:
            dark ? const Color(0xff1e1e2e) : const Color(0xff1a1a1a),
        foregroundColor: accent,
        elevation: 0,
      ),
    );
  }
}

/// Central app state: machines list, settings, ping & SSH services.
class AppState extends ChangeNotifier {
  final _machineRepo = MachineRepository();
  final _settingsRepo = SettingsRepository();
  final pingService = PingService();
  final sshService = SshService();

  List<Machine> _machines = [];
  Settings _settings = const Settings();

  List<Machine> get machines => _machines;
  Settings get settings => _settings;

  AppState() {
    _init();
  }

  Future<void> _init() async {
    _settings = await _settingsRepo.load();
    _machines = await _machineRepo.all();
    _startPing();
    notifyListeners();
  }

  void _startPing() {
    pingService.start(
        _machines.map((m) => (id: m.id, ip: m.ip, port: m.vncPort)).toList());
  }

  Future<void> addMachine(Machine m, String password) async {
    await _machineRepo.insert(m, password);
    _machines = await _machineRepo.all();
    pingService.addMachine(m.id, m.ip, m.vncPort);
    notifyListeners();
  }

  Future<void> updateMachine(Machine m, String? password) async {
    await _machineRepo.update(m, password);
    _machines = await _machineRepo.all();
    _startPing();
    notifyListeners();
  }

  Future<void> deleteMachine(String id) async {
    await sshService.disconnect(id);
    await _machineRepo.delete(id);
    _machines = await _machineRepo.all();
    pingService.removeMachine(id);
    notifyListeners();
  }

  Future<String> getPassword(String machineId) =>
      _machineRepo.getPassword(machineId);

  Future<void> saveSettings(Settings s) async {
    _settings = s;
    await _settingsRepo.save(s);
    notifyListeners();
  }

  @override
  void dispose() {
    pingService.dispose();
    sshService.disconnectAll();
    super.dispose();
  }
}
