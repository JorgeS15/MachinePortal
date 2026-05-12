import 'package:uuid/uuid.dart';

class Machine {
  final String id;
  final String name;
  final String ip;
  final bool ssh;
  final String sshUser;
  final int sshPort;
  final int vncPort;

  Machine({
    String? id,
    required this.name,
    required this.ip,
    this.ssh = false,
    this.sshUser = 'user',
    this.sshPort = 22,
    this.vncPort = 5900,
  }) : id = id ?? const Uuid().v4();

  Machine copyWith({
    String? name,
    String? ip,
    bool? ssh,
    String? sshUser,
    int? sshPort,
    int? vncPort,
  }) {
    return Machine(
      id: id,
      name: name ?? this.name,
      ip: ip ?? this.ip,
      ssh: ssh ?? this.ssh,
      sshUser: sshUser ?? this.sshUser,
      sshPort: sshPort ?? this.sshPort,
      vncPort: vncPort ?? this.vncPort,
    );
  }

  Map<String, dynamic> toMap() => {
        'id': id,
        'name': name,
        'ip': ip,
        'ssh': ssh ? 1 : 0,
        'ssh_user': sshUser,
        'ssh_port': sshPort,
        'vnc_port': vncPort,
      };

  factory Machine.fromMap(Map<String, dynamic> map) => Machine(
        id: map['id'] as String,
        name: map['name'] as String,
        ip: map['ip'] as String,
        ssh: (map['ssh'] as int) == 1,
        sshUser: map['ssh_user'] as String? ?? 'user',
        sshPort: map['ssh_port'] as int? ?? 22,
        vncPort: map['vnc_port'] as int? ?? 5900,
      );
}

class Settings {
  final int tunnelWaitMs;
  final String defaultSshUser;
  final String theme;

  const Settings({
    this.tunnelWaitMs = 1500,
    this.defaultSshUser = '',
    this.theme = 'light',
  });

  Settings copyWith({
    int? tunnelWaitMs,
    String? defaultSshUser,
    String? theme,
  }) {
    return Settings(
      tunnelWaitMs: tunnelWaitMs ?? this.tunnelWaitMs,
      defaultSshUser: defaultSshUser ?? this.defaultSshUser,
      theme: theme ?? this.theme,
    );
  }
}
