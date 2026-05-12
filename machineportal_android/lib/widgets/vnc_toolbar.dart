import 'package:flutter/material.dart';

class VncToolbar extends StatelessWidget {
  final String machineName;
  final VoidCallback onDisconnect;
  final VoidCallback onShowKeyboard;

  const VncToolbar({
    super.key,
    required this.machineName,
    required this.onDisconnect,
    required this.onShowKeyboard,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black54,
      padding: EdgeInsets.only(
        top: MediaQuery.of(context).padding.top + 4,
        left: 8,
        right: 8,
        bottom: 4,
      ),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: onDisconnect,
            tooltip: 'Disconnect',
          ),
          const SizedBox(width: 4),
          Expanded(
            child: Text(
              machineName,
              style: const TextStyle(
                  color: Colors.white, fontWeight: FontWeight.bold),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          IconButton(
            icon: const Icon(Icons.keyboard, color: Colors.white),
            onPressed: onShowKeyboard,
            tooltip: 'Keyboard',
          ),
        ],
      ),
    );
  }
}
