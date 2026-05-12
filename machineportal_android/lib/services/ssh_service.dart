import 'dart:async';
import 'dart:io';

import 'package:dartssh2/dartssh2.dart';

import '../models/machine.dart';

class ActiveTunnel {
  final SSHClient client;
  final ServerSocket localServer;
  final int localPort;

  ActiveTunnel({
    required this.client,
    required this.localServer,
    required this.localPort,
  });
}

class SshService {
  final _tunnels = <String, ActiveTunnel>{};

  /// Opens an SSH tunnel and returns the local port that proxies to the
  /// machine's VNC port. Throws on connection or auth failure.
  Future<int> connect(Machine machine, String password) async {
    if (_tunnels.containsKey(machine.id)) {
      return _tunnels[machine.id]!.localPort;
    }

    final client = SSHClient(
      await SSHSocket.connect(machine.ip, machine.sshPort,
          timeout: const Duration(seconds: 10)),
      username: machine.sshUser,
      onPasswordRequest: () => password,
    );

    // Wait for authentication to complete
    await client.authenticated;

    // Bind a local TCP server on an OS-assigned port
    final localServer = await ServerSocket.bind(InternetAddress.loopbackIPv4, 0);
    final localPort = localServer.port;

    // Accept connections and forward them through the SSH tunnel
    localServer.listen((socket) async {
      try {
        final forward = await client.forwardLocal(
          'localhost',
          machine.vncPort,
        );
        // Pipe data bidirectionally
        unawaited(socket.addStream(forward.stream));
        unawaited(forward.sink.addStream(socket));
        socket.done.whenComplete(() => forward.sink.close());
      } catch (_) {
        socket.destroy();
      }
    });

    _tunnels[machine.id] = ActiveTunnel(
      client: client,
      localServer: localServer,
      localPort: localPort,
    );

    return localPort;
  }

  Future<void> disconnect(String machineId) async {
    final tunnel = _tunnels.remove(machineId);
    if (tunnel == null) return;
    await tunnel.localServer.close();
    tunnel.client.close();
  }

  bool isConnected(String machineId) => _tunnels.containsKey(machineId);

  int? localPort(String machineId) => _tunnels[machineId]?.localPort;

  Future<void> disconnectAll() async {
    final ids = _tunnels.keys.toList();
    for (final id in ids) {
      await disconnect(id);
    }
  }
}
