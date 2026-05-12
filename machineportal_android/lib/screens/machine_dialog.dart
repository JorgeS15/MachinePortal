import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../main.dart';
import '../models/machine.dart';

/// Bottom-sheet dialog for adding or editing a machine.
class MachineDialog extends StatefulWidget {
  final Machine? existing;

  const MachineDialog({super.key, this.existing});

  static Future<void> show(BuildContext context, {Machine? existing}) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (_) => MachineDialog(existing: existing),
    );
  }

  @override
  State<MachineDialog> createState() => _MachineDialogState();
}

class _MachineDialogState extends State<MachineDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _name;
  late TextEditingController _ip;
  late TextEditingController _sshUser;
  late TextEditingController _sshPassword;
  late TextEditingController _sshPort;
  late TextEditingController _vncPort;
  late bool _ssh;
  bool _passwordVisible = false;
  bool _loading = false;

  bool get _isEdit => widget.existing != null;

  @override
  void initState() {
    super.initState();
    final app = context.read<AppState>();
    final m = widget.existing;
    _name = TextEditingController(text: m?.name ?? '');
    _ip = TextEditingController(text: m?.ip ?? '');
    _sshUser = TextEditingController(
        text: m?.sshUser ?? app.settings.defaultSshUser);
    _sshPassword = TextEditingController();
    _sshPort = TextEditingController(text: m?.sshPort.toString() ?? '22');
    _vncPort = TextEditingController(text: m?.vncPort.toString() ?? '5900');
    _ssh = m?.ssh ?? false;

    if (_isEdit && m!.ssh) {
      // Load existing password for display
      app.getPassword(m.id).then((pw) {
        if (mounted) _sshPassword.text = pw;
      });
    }
  }

  @override
  void dispose() {
    for (final c in [_name, _ip, _sshUser, _sshPassword, _sshPort, _vncPort]) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);

    final app = context.read<AppState>();
    final machine = Machine(
      id: widget.existing?.id,
      name: _name.text.trim(),
      ip: _ip.text.trim(),
      ssh: _ssh,
      sshUser: _sshUser.text.trim(),
      sshPort: int.parse(_sshPort.text),
      vncPort: int.parse(_vncPort.text),
    );

    try {
      if (_isEdit) {
        await app.updateMachine(
            machine, _ssh ? _sshPassword.text : null);
      } else {
        await app.addMachine(machine, _sshPassword.text);
      }
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 24, 16, 24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                _isEdit ? 'Edit Machine' : 'Add Machine',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 20),
              _field(_name, 'Name', required: true),
              const SizedBox(height: 12),
              _field(_ip, 'IP Address',
                  required: true,
                  hint: '192.168.1.100',
                  keyboard: TextInputType.numberWithOptions(decimal: true)),
              const SizedBox(height: 12),
              _field(_vncPort, 'VNC Port',
                  keyboard: TextInputType.number, required: true),
              const SizedBox(height: 16),
              // SSH toggle
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Use SSH Tunnel'),
                value: _ssh,
                onChanged: (v) => setState(() => _ssh = v),
              ),
              if (_ssh) ...[
                const SizedBox(height: 8),
                _field(_sshUser, 'SSH User', required: _ssh),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _sshPassword,
                  obscureText: !_passwordVisible,
                  decoration: InputDecoration(
                    labelText: 'SSH Password',
                    border: const OutlineInputBorder(),
                    suffixIcon: IconButton(
                      icon: Icon(_passwordVisible
                          ? Icons.visibility_off
                          : Icons.visibility),
                      onPressed: () =>
                          setState(() => _passwordVisible = !_passwordVisible),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                _field(_sshPort, 'SSH Port',
                    keyboard: TextInputType.number, required: _ssh),
              ],
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _loading ? null : _save,
                child: _loading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2))
                    : Text(_isEdit ? 'Save Changes' : 'Add Machine'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _field(TextEditingController c, String label,
      {bool required = false,
      String? hint,
      TextInputType keyboard = TextInputType.text}) {
    return TextFormField(
      controller: c,
      keyboardType: keyboard,
      inputFormatters: keyboard == TextInputType.number
          ? [FilteringTextInputFormatter.digitsOnly]
          : null,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        border: const OutlineInputBorder(),
      ),
      validator: required
          ? (v) => v == null || v.trim().isEmpty ? '$label is required' : null
          : null,
    );
  }
}
