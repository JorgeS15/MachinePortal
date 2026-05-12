import 'package:flutter/material.dart';

import '../models/machine.dart';
import '../services/ping_service.dart';

class MachineCard extends StatelessWidget {
  final Machine machine;
  final PingState pingState;
  final bool connected;
  final VoidCallback onTap;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const MachineCard({
    super.key,
    required this.machine,
    required this.pingState,
    required this.connected,
    required this.onTap,
    required this.onEdit,
    required this.onDelete,
  });

  Color _pingColor() => switch (pingState) {
        PingState.online => const Color(0xff4caf50),
        PingState.offline => const Color(0xfff44336),
        PingState.unknown => const Color(0xff9e9e9e),
      };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final accent = theme.colorScheme.primary;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Monitor thumbnail
              _MonitorIcon(
                accent: accent,
                connected: connected,
              ),
              const SizedBox(height: 10),
              // Machine name
              Text(
                machine.name,
                style: theme.textTheme.titleSmall
                    ?.copyWith(fontWeight: FontWeight.bold),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 2),
              // IP address
              Text(
                machine.ip,
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
              ),
              const SizedBox(height: 8),
              // Status row: ping dot + SSH badge + action menu
              Row(
                children: [
                  // Ping dot
                  Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: _pingColor(),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 6),
                  if (machine.ssh)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: accent.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        'SSH',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: accent,
                        ),
                      ),
                    ),
                  const Spacer(),
                  // Action menu (⋮)
                  SizedBox(
                    width: 32,
                    height: 32,
                    child: PopupMenuButton<_Action>(
                      padding: EdgeInsets.zero,
                      icon: Icon(Icons.more_vert,
                          size: 18,
                          color: theme.colorScheme.onSurfaceVariant),
                      onSelected: (a) {
                        if (a == _Action.edit) onEdit();
                        if (a == _Action.delete) onDelete();
                      },
                      itemBuilder: (_) => const [
                        PopupMenuItem(
                          value: _Action.edit,
                          child: Text('Edit'),
                        ),
                        PopupMenuItem(
                          value: _Action.delete,
                          child: Text('Delete'),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

enum _Action { edit, delete }

class _MonitorIcon extends StatelessWidget {
  final Color accent;
  final bool connected;

  const _MonitorIcon({required this.accent, required this.connected});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: const Size(80, 60),
      painter: _MonitorPainter(accent: accent, connected: connected),
    );
  }
}

class _MonitorPainter extends CustomPainter {
  final Color accent;
  final bool connected;

  _MonitorPainter({required this.accent, required this.connected});

  @override
  void paint(Canvas canvas, Size size) {
    final borderPaint = Paint()
      ..color = accent
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    final screenPaint = Paint()
      ..color = connected ? accent.withValues(alpha: 0.25) : Colors.black54
      ..style = PaintingStyle.fill;

    // Screen bezel
    final bezel = RRect.fromRectAndRadius(
      Rect.fromLTWH(0, 0, size.width, size.height * 0.78),
      const Radius.circular(4),
    );
    canvas.drawRRect(bezel, screenPaint);
    canvas.drawRRect(bezel, borderPaint);

    // Stand stem
    final stemX = size.width / 2;
    canvas.drawLine(
      Offset(stemX, size.height * 0.78),
      Offset(stemX, size.height * 0.90),
      borderPaint,
    );
    // Stand base
    canvas.drawLine(
      Offset(stemX - 12, size.height * 0.90),
      Offset(stemX + 12, size.height * 0.90),
      borderPaint,
    );
  }

  @override
  bool shouldRepaint(_MonitorPainter old) =>
      old.accent != accent || old.connected != connected;
}
