import 'dart:ui' as ui;

import 'package:flutter/material.dart';

import '../services/vnc/rfb_client.dart';

/// Renders a VNC framebuffer onto a Flutter canvas.
class VncPainter extends CustomPainter {
  final RfbFramebuffer framebuffer;
  final ui.Image? image;

  VncPainter({required this.framebuffer, this.image});

  @override
  void paint(Canvas canvas, Size size) {
    if (image == null) {
      canvas.drawRect(
        Rect.fromLTWH(0, 0, size.width, size.height),
        Paint()..color = Colors.black,
      );
      return;
    }

    final src = Rect.fromLTWH(
      0, 0, framebuffer.width.toDouble(), framebuffer.height.toDouble());
    final dst = Rect.fromLTWH(0, 0, size.width, size.height);
    canvas.drawImageRect(image!, src, dst, Paint());
  }

  @override
  bool shouldRepaint(VncPainter old) => old.image != image;
}

/// Widget that manages converting raw pixel bytes → ui.Image and painting.
class VncCanvas extends StatefulWidget {
  final Stream<RfbFramebuffer> frames;
  final int fbWidth;
  final int fbHeight;

  const VncCanvas({
    super.key,
    required this.frames,
    required this.fbWidth,
    required this.fbHeight,
  });

  @override
  State<VncCanvas> createState() => _VncCanvasState();
}

class _VncCanvasState extends State<VncCanvas> {
  ui.Image? _image;

  @override
  void initState() {
    super.initState();
    widget.frames.listen(_onFrame);
  }

  Future<void> _onFrame(RfbFramebuffer fb) async {
    final img = await _decodeImage(fb);
    if (mounted) {
      setState(() => _image = img);
    }
  }

  Future<ui.Image> _decodeImage(RfbFramebuffer fb) async {
    final codec = await ui.ImageDescriptor.raw(
      await ui.ImmutableBuffer.fromUint8List(fb.pixels),
      width: fb.width,
      height: fb.height,
      pixelFormat: ui.PixelFormat.rgba8888,
    ).instantiateCodec();
    final frame = await codec.getNextFrame();
    return frame.image;
  }

  @override
  void dispose() {
    _image?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_image == null) {
      return const Center(
          child: CircularProgressIndicator());
    }
    return CustomPaint(
      painter: VncPainter(
        framebuffer: RfbFramebuffer(widget.fbWidth, widget.fbHeight),
        image: _image,
      ),
      child: const SizedBox.expand(),
    );
  }
}
