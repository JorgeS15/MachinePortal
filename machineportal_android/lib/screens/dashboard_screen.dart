import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../main.dart';
import '../models/machine.dart';
import '../services/ping_service.dart';
import '../widgets/machine_card.dart';
import 'machine_dialog.dart';
import 'settings_screen.dart';
import 'vnc_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  // Latest ping states — updated from PingService stream
  Map<String, PingState> _pingStates = {};

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final ping = context.read<AppState>().pingService;
      _pingStates = ping.states;
      ping.stream.listen((states) {
        if (mounted) setState(() => _pingStates = states);
      });
    });
  }

  Future<bool> _confirmDelete(BuildContext context, Machine m) async {
    return await showDialog<bool>(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Delete Machine'),
            content: Text('Remove "${m.name}" from the list?'),
            actions: [
              TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text('Cancel')),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                style: FilledButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.error),
                child: const Text('Delete'),
              ),
            ],
          ),
        ) ??
        false;
  }

  void _openVnc(Machine m) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => VncScreen(machine: m)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, app, child) {
        final machines = app.machines;

        return Scaffold(
          appBar: AppBar(
            title: Row(
              children: [
                Icon(Icons.computer,
                    color: Theme.of(context).colorScheme.primary, size: 22),
                const SizedBox(width: 8),
                const Text('MachinePortal',
                    style: TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.settings_outlined),
                tooltip: 'Settings',
                onPressed: () => Navigator.push(context,
                    MaterialPageRoute(builder: (_) => const SettingsScreen())),
              ),
              IconButton(
                icon: const Icon(Icons.add),
                tooltip: 'Add Machine',
                onPressed: () => MachineDialog.show(context),
              ),
            ],
          ),
          body: machines.isEmpty
              ? _buildEmpty(context)
              : _buildGrid(context, app, machines),
        );
      },
    );
  }

  Widget _buildEmpty(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.computer_outlined,
              size: 64, color: Theme.of(context).colorScheme.outlineVariant),
          const SizedBox(height: 16),
          Text('No machines yet',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant)),
          const SizedBox(height: 8),
          Text('Tap + to add your first machine',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant)),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: () => MachineDialog.show(context),
            icon: const Icon(Icons.add),
            label: const Text('Add Machine'),
          ),
        ],
      ),
    );
  }

  Widget _buildGrid(BuildContext context, AppState app, List<Machine> machines) {
    return LayoutBuilder(
      builder: (_, constraints) {
        // 2 columns for most phones (< 600 px wide), more for tablets
        final cols = constraints.maxWidth < 600
            ? 2
            : constraints.maxWidth < 900
                ? 3
                : 4;

        return GridView.builder(
          padding: const EdgeInsets.all(12),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: cols,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
            childAspectRatio: 0.85,
          ),
          itemCount: machines.length,
          itemBuilder: (_, i) {
            final m = machines[i];
            final ping = _pingStates[m.id] ?? PingState.unknown;
            final connected = app.sshService.isConnected(m.id);

            return MachineCard(
              machine: m,
              pingState: ping,
              connected: connected,
              onTap: () => _openVnc(m),
              onEdit: () => MachineDialog.show(context, existing: m),
              onDelete: () async {
                final ok = await _confirmDelete(context, m);
                if (ok && context.mounted) {
                  await app.deleteMachine(m.id);
                }
              },
            );
          },
        );
      },
    );
  }
}
