import 'package:shared_preferences/shared_preferences.dart';
import '../models/machine.dart';

class SettingsRepository {
  static const _keyTunnelWait = 'tunnel_wait_ms';
  static const _keyDefaultUser = 'default_ssh_user';
  static const _keyTheme = 'theme';

  Future<Settings> load() async {
    final prefs = await SharedPreferences.getInstance();
    return Settings(
      tunnelWaitMs: prefs.getInt(_keyTunnelWait) ?? 1500,
      defaultSshUser: prefs.getString(_keyDefaultUser) ?? '',
      theme: prefs.getString(_keyTheme) ?? 'light',
    );
  }

  Future<void> save(Settings s) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_keyTunnelWait, s.tunnelWaitMs);
    await prefs.setString(_keyDefaultUser, s.defaultSshUser);
    await prefs.setString(_keyTheme, s.theme);
  }
}
