import 'dart:async';
import 'dart:io';

enum PingState { unknown, online, offline }

class PingService {
  static const _interval = Duration(seconds: 5);
  static const _timeout = Duration(seconds: 1);

  final _state = <String, PingState>{};
  final _controller = StreamController<Map<String, PingState>>.broadcast();
  Timer? _timer;

  /// Snapshot of all current ping states.
  Map<String, PingState> get states => Map.unmodifiable(_state);

  /// Emits a new map on every probe cycle.
  Stream<Map<String, PingState>> get stream => _controller.stream;

  /// Start probing [machines] — list of (id, ip, port) records.
  void start(List<({String id, String ip, int port})> machines) {
    _timer?.cancel();
    for (final m in machines) {
      _state.putIfAbsent(m.id, () => PingState.unknown);
    }
    _timer = Timer.periodic(_interval, (_) => _probe(machines));
    // Probe immediately
    _probe(machines);
  }

  void stop() {
    _timer?.cancel();
    _timer = null;
  }

  void addMachine(String id, String ip, int port) {
    _state.putIfAbsent(id, () => PingState.unknown);
  }

  void removeMachine(String id) {
    _state.remove(id);
  }

  Future<void> _probe(List<({String id, String ip, int port})> machines) async {
    final results = await Future.wait(
      machines.map((m) => _tcpPing(m.id, m.ip, m.port)),
    );
    for (final r in results) {
      _state[r.$1] = r.$2;
    }
    _controller.add(Map.unmodifiable(_state));
  }

  Future<(String, PingState)> _tcpPing(
      String id, String ip, int port) async {
    try {
      final s = await Socket.connect(ip, port, timeout: _timeout);
      await s.close();
      return (id, PingState.online);
    } catch (_) {
      return (id, PingState.offline);
    }
  }

  void dispose() {
    stop();
    _controller.close();
  }
}
