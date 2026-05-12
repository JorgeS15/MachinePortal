import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../main.dart';
import '../models/machine.dart';
import '../services/vnc/rfb_client.dart';
import '../services/vnc/rfb_input.dart';
import '../widgets/vnc_painter.dart';
import '../widgets/vnc_toolbar.dart';

class VncScreen extends StatefulWidget {
  final Machine machine;

  const VncScreen({super.key, required this.machine});

  @override
  State<VncScreen> createState() => _VncScreenState();
}

class _VncScreenState extends State<VncScreen> {
  RfbClient? _rfb;
  RfbState _state = RfbState.connecting;
  String? _error;

  // Framebuffer dimensions once connected
  int _fbW = 1, _fbH = 1;

  // Track scale for coordinate mapping: canvas → framebuffer
  final _canvasKey = GlobalKey();
  Size _canvasSize = Size.zero;

  // Track pointer state for drag events
  bool _pointerDown = false;

  // Keep toolbar visible for 3 s then fade
  bool _toolbarVisible = true;
  Timer? _toolbarTimer;

  @override
  void initState() {
    super.initState();
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersive);
    _connect();
  }

  Future<void> _connect() async {
    final app = context.read<AppState>();
    final m = widget.machine;

    String host = m.ip;
    int port = m.vncPort;

    if (m.ssh) {
      try {
        final pw = await app.getPassword(m.id);
        final wait = app.settings.tunnelWaitMs;
        final localPort = await app.sshService.connect(m, pw);
        await Future.delayed(Duration(milliseconds: wait));
        host = '127.0.0.1';
        port = localPort;
      } catch (e) {
        if (mounted) {
          setState(() {
            _state = RfbState.error;
            _error = 'SSH error: $e';
          });
        }
        return;
      }
    }

    final password = m.ssh ? '' : await app.getPassword(m.id);
    _rfb = RfbClient(host: host, port: port, password: password.isEmpty ? null : password);

    _rfb!.stateChanges.listen((s) {
      if (mounted) setState(() => _state = s);
    });

    try {
      await _rfb!.connect();
      if (mounted) {
        setState(() {
          _fbW = _rfb!.framebuffer.width;
          _fbH = _rfb!.framebuffer.height;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _state = RfbState.error;
          _error = e.toString();
        });
      }
    }
  }

  void _disconnect() {
    _rfb?.dispose();
    final app = context.read<AppState>();
    if (widget.machine.ssh) {
      app.sshService.disconnect(widget.machine.id);
    }
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
    if (mounted) Navigator.pop(context);
  }

  void _showToolbar() {
    setState(() => _toolbarVisible = true);
    _toolbarTimer?.cancel();
    _toolbarTimer = Timer(const Duration(seconds: 3), () {
      if (mounted) setState(() => _toolbarVisible = false);
    });
  }

  // Convert canvas coordinates to framebuffer coordinates
  (int, int) _toFb(Offset local) {
    if (_canvasSize == Size.zero) return (0, 0);
    final x = (local.dx / _canvasSize.width * _fbW).round().clamp(0, _fbW - 1);
    final y = (local.dy / _canvasSize.height * _fbH).round().clamp(0, _fbH - 1);
    return (x, y);
  }

  void _onTapDown(TapDownDetails d) {
    if (_rfb?.state != RfbState.connected) return;
    final (x, y) = _toFb(d.localPosition);
    _rfb!.input.click(x, y);
  }

  void _onLongPress(LongPressStartDetails d) {
    if (_rfb?.state != RfbState.connected) return;
    HapticFeedback.mediumImpact();
    final (x, y) = _toFb(d.localPosition);
    _rfb!.input.rightClick(x, y);
  }

  void _onPanStart(DragStartDetails d) {
    if (_rfb?.state != RfbState.connected) return;
    final (x, y) = _toFb(d.localPosition);
    _rfb!.input.pointerEvent(x, y, buttons: 1);
    _pointerDown = true;
  }

  void _onPanUpdate(DragUpdateDetails d) {
    if (_rfb?.state != RfbState.connected || !_pointerDown) return;
    final (x, y) = _toFb(d.localPosition);
    _rfb!.input.pointerEvent(x, y, buttons: 1);
  }

  void _onPanEnd(DragEndDetails _) {
    if (!_pointerDown) return;
    _pointerDown = false;
    // Release at last known position — we'll approximate with 0,0 move
    _rfb?.input.pointerEvent(0, 0, buttons: 0);
  }

  void _showKeyboard() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (_) => _KeyboardSheet(rfb: _rfb),
    );
  }

  @override
  void dispose() {
    _toolbarTimer?.cancel();
    _rfb?.dispose();
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: GestureDetector(
        onTap: _showToolbar,
        onTapDown: _onTapDown,
        onLongPressStart: _onLongPress,
        onPanStart: _onPanStart,
        onPanUpdate: _onPanUpdate,
        onPanEnd: _onPanEnd,
        child: Stack(
          children: [
            // VNC canvas
            LayoutBuilder(
              builder: (_, constraints) {
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  _canvasSize =
                      Size(constraints.maxWidth, constraints.maxHeight);
                });
                if (_rfb != null && _state == RfbState.connected) {
                  return VncCanvas(
                    key: _canvasKey,
                    frames: _rfb!.frames,
                    fbWidth: _fbW,
                    fbHeight: _fbH,
                  );
                }
                return _buildOverlay();
              },
            ),
            // Toolbar (fades in/out)
            AnimatedOpacity(
              opacity: _toolbarVisible ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 300),
              child: VncToolbar(
                machineName: widget.machine.name,
                onDisconnect: _disconnect,
                onShowKeyboard: _showKeyboard,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverlay() {
    return Center(
      child: switch (_state) {
        RfbState.connecting || RfbState.handshaking => Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(color: Colors.white),
              const SizedBox(height: 16),
              Text(
                widget.machine.ssh
                    ? 'Opening SSH tunnel…'
                    : 'Connecting to VNC…',
                style: const TextStyle(color: Colors.white),
              ),
            ],
          ),
        RfbState.error => Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, color: Colors.red, size: 48),
              const SizedBox(height: 12),
              Text(_error ?? 'Connection failed',
                  style: const TextStyle(color: Colors.white),
                  textAlign: TextAlign.center),
              const SizedBox(height: 16),
              TextButton(
                onPressed: _disconnect,
                child: const Text('Go Back',
                    style: TextStyle(color: Colors.white70)),
              ),
            ],
          ),
        RfbState.disconnected => Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.link_off, color: Colors.white54, size: 48),
              const SizedBox(height: 12),
              const Text('Disconnected',
                  style: TextStyle(color: Colors.white70)),
              const SizedBox(height: 16),
              TextButton(
                onPressed: _disconnect,
                child: const Text('Go Back',
                    style: TextStyle(color: Colors.white70)),
              ),
            ],
          ),
        _ => const SizedBox.shrink(),
      },
    );
  }
}

class _KeyboardSheet extends StatefulWidget {
  final RfbClient? rfb;
  const _KeyboardSheet({this.rfb});

  @override
  State<_KeyboardSheet> createState() => _KeyboardSheetState();
}

class _KeyboardSheetState extends State<_KeyboardSheet> {
  final _ctrl = TextEditingController();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
        top: 16,
        left: 16,
        right: 16,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _ctrl,
                  autofocus: true,
                  decoration: const InputDecoration(
                    labelText: 'Type text to send',
                    border: OutlineInputBorder(),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              FilledButton(
                onPressed: () {
                  widget.rfb?.input.sendString(_ctrl.text);
                  _ctrl.clear();
                  Navigator.pop(context);
                },
                child: const Text('Send'),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _keyBtn('Enter', () => widget.rfb?.input.keyEvent(
                  RfbInput.ksReturn, down: true)),
              _keyBtn('Esc', () => widget.rfb?.input.keyEvent(
                  RfbInput.ksEscape, down: true)),
              _keyBtn('Tab', () => widget.rfb?.input.keyEvent(
                  RfbInput.ksTab, down: true)),
              _keyBtn('Bksp', () => widget.rfb?.input.keyEvent(
                  RfbInput.ksBackspace, down: true)),
              _keyBtn('←', () => widget.rfb?.input.keyEvent(
                  RfbInput.ksLeft, down: true)),
              _keyBtn('→', () => widget.rfb?.input.keyEvent(
                  RfbInput.ksRight, down: true)),
              _keyBtn('↑', () => widget.rfb?.input.keyEvent(
                  RfbInput.ksUp, down: true)),
              _keyBtn('↓', () => widget.rfb?.input.keyEvent(
                  RfbInput.ksDown, down: true)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _keyBtn(String label, VoidCallback onTap) {
    return OutlinedButton(
      onPressed: onTap,
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(56, 44),
        padding: const EdgeInsets.symmetric(horizontal: 8),
      ),
      child: Text(label),
    );
  }
}
