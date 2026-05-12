import 'dart:typed_data';
import 'dart:io';

import 'rfb_client.dart';

/// Handles compressed RFB encodings (Zlib and ZRLE).
class RfbDecoder {
  // Zlib inflate state persists across rectangles (shared deflate context)
  final _zlibContext = _ZlibContext();

  bool decodeZlib(BytesBuilder buf, int x, int y, int w, int h,
      RfbFramebuffer fb) {
    if (buf.length < 4) return false;
    final all = buf.takeBytes();
    final bd = ByteData.sublistView(all);
    final dataLen = bd.getUint32(0);
    if (all.length < 4 + dataLen) {
      buf.add(all);
      return false;
    }
    final compressed = all.sublist(4, 4 + dataLen);
    if (all.length > 4 + dataLen) buf.add(all.sublist(4 + dataLen));

    final raw = _zlibContext.inflate(compressed);
    _applyRaw(raw, x, y, w, h, fb);
    return true;
  }

  bool decodeZrle(BytesBuilder buf, int x, int y, int w, int h,
      RfbFramebuffer fb) {
    if (buf.length < 4) return false;
    final all = buf.takeBytes();
    final bd = ByteData.sublistView(all);
    final dataLen = bd.getUint32(0);
    if (all.length < 4 + dataLen) {
      buf.add(all);
      return false;
    }
    final compressed = all.sublist(4, 4 + dataLen);
    if (all.length > 4 + dataLen) buf.add(all.sublist(4 + dataLen));

    final raw = _zlibContext.inflate(compressed);
    _decodeZrleTiles(raw, x, y, w, h, fb);
    return true;
  }

  void _applyRaw(Uint8List raw, int x, int y, int w, int h,
      RfbFramebuffer fb) {
    var i = 0;
    for (var row = y; row < y + h; row++) {
      final base = (row * fb.width + x) * 4;
      for (var col = 0; col < w; col++) {
        fb.pixels[base + col * 4] = raw[i + 2];     // R
        fb.pixels[base + col * 4 + 1] = raw[i + 1]; // G
        fb.pixels[base + col * 4 + 2] = raw[i];     // B
        fb.pixels[base + col * 4 + 3] = 0xff;
        i += 4;
      }
    }
  }

  void _decodeZrleTiles(Uint8List data, int rx, int ry, int rw, int rh,
      RfbFramebuffer fb) {
    var pos = 0;

    int readByte() => data[pos++];
    int readPixel() {
      // CPIXEL: 3 bytes when bits-per-pixel is 32 (compact pixel)
      final b = data[pos]; final g = data[pos+1]; final r = data[pos+2];
      pos += 3;
      return (0xff000000) | (r << 16) | (g << 8) | b;
    }

    for (var ty = ry; ty < ry + rh; ty += 64) {
      for (var tx = rx; tx < rx + rw; tx += 64) {
        final tw = (tx + 64 > rx + rw) ? rx + rw - tx : 64;
        final th = (ty + 64 > ry + rh) ? ry + rh - ty : 64;

        if (pos >= data.length) break;
        final subtype = readByte();

        if (subtype == 0) {
          // Raw tile
          for (var row = ty; row < ty + th; row++) {
            final base = (row * fb.width + tx) * 4;
            for (var col = 0; col < tw; col++) {
              final argb = readPixel();
              fb.pixels[base + col * 4] = (argb >> 16) & 0xff;
              fb.pixels[base + col * 4 + 1] = (argb >> 8) & 0xff;
              fb.pixels[base + col * 4 + 2] = argb & 0xff;
              fb.pixels[base + col * 4 + 3] = 0xff;
            }
          }
        } else if (subtype == 1) {
          // Solid tile
          final argb = readPixel();
          final r = (argb >> 16) & 0xff;
          final g = (argb >> 8) & 0xff;
          final b = argb & 0xff;
          fb.fillRect(tx, ty, tw, th, (r << 16) | (g << 8) | b);
        } else if (subtype >= 2 && subtype <= 16) {
          // Packed palette
          final paletteSize = subtype;
          final palette = <int>[];
          for (var i = 0; i < paletteSize; i++) {
            palette.add(readPixel());
          }
          final bpp = paletteSize <= 2 ? 1 : paletteSize <= 4 ? 2 : 4;
          for (var row = ty; row < ty + th; row++) {
            final base = (row * fb.width + tx) * 4;
            var bitPos = 0;
            var byteVal = 0;
            for (var col = 0; col < tw; col++) {
              if (bitPos == 0) {
                byteVal = readByte();
                bitPos = 8;
              }
              bitPos -= bpp;
              final idx = (byteVal >> bitPos) & ((1 << bpp) - 1);
              final argb = idx < palette.length ? palette[idx] : 0xff000000;
              fb.pixels[base + col * 4] = (argb >> 16) & 0xff;
              fb.pixels[base + col * 4 + 1] = (argb >> 8) & 0xff;
              fb.pixels[base + col * 4 + 2] = argb & 0xff;
              fb.pixels[base + col * 4 + 3] = 0xff;
            }
          }
        } else if (subtype == 128) {
          // Plain RLE
          var px = tx; var py = ty;
          while (py < ty + th) {
            final argb = readPixel();
            final r = (argb >> 16) & 0xff;
            final g = (argb >> 8) & 0xff;
            final b = argb & 0xff;
            var runLen = 1;
            while (data[pos] == 255) { runLen += 255; pos++; }
            runLen += readByte();
            for (var i = 0; i < runLen; i++) {
              final base = (py * fb.width + px) * 4;
              fb.pixels[base] = r;
              fb.pixels[base + 1] = g;
              fb.pixels[base + 2] = b;
              fb.pixels[base + 3] = 0xff;
              px++;
              if (px >= tx + tw) { px = tx; py++; }
            }
          }
        } else if (subtype >= 130) {
          // Palette RLE
          final paletteSize = subtype - 128;
          final palette = <int>[];
          for (var i = 0; i < paletteSize; i++) {
            palette.add(readPixel());
          }
          var px = tx; var py = ty;
          while (py < ty + th) {
            final idx = readByte();
            final isRle = (idx & 0x80) != 0;
            final argb = palette[idx & 0x7f];
            final r = (argb >> 16) & 0xff;
            final g = (argb >> 8) & 0xff;
            final b = argb & 0xff;
            var runLen = 1;
            if (isRle) {
              while (data[pos] == 255) { runLen += 255; pos++; }
              runLen += readByte();
            }
            for (var i = 0; i < runLen; i++) {
              final base = (py * fb.width + px) * 4;
              fb.pixels[base] = r;
              fb.pixels[base + 1] = g;
              fb.pixels[base + 2] = b;
              fb.pixels[base + 3] = 0xff;
              px++;
              if (px >= tx + tw) { px = tx; py++; }
            }
          }
        }
      }
    }
  }
}

class _ZlibContext {
  late ZLibDecoder _decoder;

  _ZlibContext() {
    _decoder = ZLibDecoder();
  }

  Uint8List inflate(Uint8List data) {
    final result = _decoder.convert(data);
    return Uint8List.fromList(result);
  }
}
