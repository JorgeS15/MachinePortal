// ignore_for_file: constant_identifier_names
import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'rfb_decoder.dart';
import 'rfb_input.dart';

enum RfbState { connecting, handshaking, connected, disconnected, error }

class RfbFramebuffer {
  final int width;
  final int height;
  // ARGB8888 pixel buffer (4 bytes per pixel, host byte order for ui.Image)
  final Uint8List pixels;

  RfbFramebuffer(this.width, this.height)
      : pixels = Uint8List(width * height * 4);

  void fillRect(int x, int y, int w, int h, int argb) {
    final r = (argb >> 16) & 0xff;
    final g = (argb >> 8) & 0xff;
    final b = argb & 0xff;
    for (var row = y; row < y + h && row < height; row++) {
      final base = (row * width + x) * 4;
      for (var col = 0; col < w && x + col < width; col++) {
        final i = base + col * 4;
        pixels[i] = r;
        pixels[i + 1] = g;
        pixels[i + 2] = b;
        pixels[i + 3] = 0xff;
      }
    }
  }

  void copyPixels(int dstX, int dstY, int w, int h, int srcX, int srcY) {
    // Copy row by row; handle overlapping regions correctly
    if (srcY < dstY) {
      for (var row = h - 1; row >= 0; row--) {
        _copyRow(dstX, dstY + row, w, srcX, srcY + row);
      }
    } else {
      for (var row = 0; row < h; row++) {
        _copyRow(dstX, dstY + row, w, srcX, srcY + row);
      }
    }
  }

  void _copyRow(int dstX, int dstY, int w, int srcX, int srcY) {
    if (srcY < 0 || srcY >= height || dstY < 0 || dstY >= height) return;
    final src = (srcY * width + srcX) * 4;
    final dst = (dstY * width + dstX) * 4;
    pixels.setRange(dst, dst + w * 4, pixels, src);
  }
}

class RfbClient {
  static const _serverInitMsgType = 2; // FramebufferUpdate
  static const _encodingRaw = 0;
  static const _encodingCopyRect = 1;
  static const _encodingZrle = 16;
  static const _encodingZlib = 6;

  final String host;
  final int port;
  final String? password;

  Socket? _socket;
  late StreamSubscription<Uint8List> _sub;
  final _buf = BytesBuilder(copy: false);
  late Completer<void> _ready;

  RfbState _state = RfbState.connecting;
  RfbState get state => _state;

  late RfbFramebuffer framebuffer;
  int _fbWidth = 0;
  int _fbHeight = 0;

  final _frameController = StreamController<RfbFramebuffer>.broadcast();
  Stream<RfbFramebuffer> get frames => _frameController.stream;

  final _stateController = StreamController<RfbState>.broadcast();
  Stream<RfbState> get stateChanges => _stateController.stream;

  late RfbInput _input;
  RfbInput get input => _input;

  final RfbDecoder _decoder = RfbDecoder();

  // Phase tracking for the handshake state machine
  _Phase _phase = _Phase.version;
  int _secType = 0;

  RfbClient({required this.host, required this.port, this.password});

  Future<void> connect() async {
    _ready = Completer<void>();
    try {
      _socket = await Socket.connect(host, port,
          timeout: const Duration(seconds: 10));
      _input = RfbInput(_socket!);

      _sub = _socket!
          .cast<Uint8List>()
          .listen(_onData, onError: _onError, onDone: _onDone);

      await _ready.future;
    } catch (e) {
      _setState(RfbState.error);
      rethrow;
    }
  }

  void _setState(RfbState s) {
    _state = s;
    _stateController.add(s);
  }

  void _onError(Object e) {
    _setState(RfbState.error);
    _frameController.addError(e);
    if (!_ready.isCompleted) _ready.completeError(e);
    dispose();
  }

  void _onDone() {
    _setState(RfbState.disconnected);
    if (!_ready.isCompleted) _ready.completeError('connection closed');
    dispose();
  }

  void _onData(Uint8List data) {
    _buf.add(data);
    _process();
  }

  Uint8List? _take(int n) {
    if (_buf.length < n) return null;
    final all = _buf.takeBytes();
    final chunk = all.sublist(0, n);
    if (all.length > n) _buf.add(all.sublist(n));
    return chunk;
  }

  void _process() {
    switch (_phase) {
      case _Phase.version:
        _handleVersion();
      case _Phase.security:
        _handleSecurity();
      case _Phase.vncAuth:
        _handleVncAuth();
      case _Phase.securityResult:
        _handleSecurityResult();
      case _Phase.serverInit:
        _handleServerInit();
      case _Phase.msgType:
        _handleMsgType();
      case _Phase.fbUpdate:
        _handleFbUpdate();
    }
  }

  // ── Handshake ──────────────────────────────────────────────────────────────

  void _handleVersion() {
    final data = _take(12);
    if (data == null) return;
    // Server sends: RFB 003.008\n — reply with same
    _socket!.add(data); // echo back; both support 3.8
    _phase = _Phase.security;
    _process();
  }

  void _handleSecurity() {
    // Read number of security types
    final header = _take(1);
    if (header == null) return;
    final nTypes = header[0];
    if (nTypes == 0) {
      _onError('server rejected connection');
      return;
    }
    final types = _take(nTypes);
    if (types == null) {
      _buf.add(header);
      return;
    }
    // Prefer VNC Auth (2), fall back to None (1)
    _secType = types.contains(2) ? 2 : 1;
    _socket!.add(Uint8List.fromList([_secType]));
    _phase = _secType == 2 ? _Phase.vncAuth : _Phase.securityResult;
    _process();
  }

  void _handleVncAuth() {
    final challenge = _take(16);
    if (challenge == null) return;
    final response = _desEncrypt(challenge, password ?? '');
    _socket!.add(response);
    _phase = _Phase.securityResult;
    _process();
  }

  void _handleSecurityResult() {
    final data = _take(4);
    if (data == null) return;
    final result = ByteData.sublistView(data).getUint32(0);
    if (result != 0) {
      _onError('VNC authentication failed');
      return;
    }
    // Send ClientInit (shared = 1)
    _socket!.add(Uint8List.fromList([1]));
    _phase = _Phase.serverInit;
    _process();
  }

  void _handleServerInit() {
    if (_buf.length < 24) return;
    final data = _take(24)!;
    final bd = ByteData.sublistView(data);
    _fbWidth = bd.getUint16(0);
    _fbHeight = bd.getUint16(2);
    // skip pixel format (16 bytes) + name length
    final nameLen = bd.getUint32(20);
    final nameData = _take(nameLen);
    if (nameData == null) {
      _buf.add(data);
      return;
    }
    framebuffer = RfbFramebuffer(_fbWidth, _fbHeight);

    // Request 32-bit ARGB pixel format
    _sendSetPixelFormat();
    // Advertise supported encodings
    _sendSetEncodings();
    // Request first full framebuffer update
    _sendFbUpdateRequest(incremental: false);

    _setState(RfbState.connected);
    _phase = _Phase.msgType;
    if (!_ready.isCompleted) _ready.complete();
    _process();
  }

  // ── Server message dispatch ────────────────────────────────────────────────

  void _handleMsgType() {
    final data = _take(1);
    if (data == null) return;
    if (data[0] == _serverInitMsgType) {
      _phase = _Phase.fbUpdate;
      _pendingRects = -1; // sentinel — need to read header
    } else {
      // Unknown message — skip (shouldn't happen with minimal encoding set)
      _phase = _Phase.msgType;
    }
    _process();
  }

  int _pendingRects = 0;
  int _rectsRead = 0;

  void _handleFbUpdate() {
    if (_pendingRects < 0) {
      // Read FramebufferUpdate header: 1 padding + 2 nRects
      final hdr = _take(3);
      if (hdr == null) return;
      _pendingRects = ByteData.sublistView(hdr).getUint16(1);
      _rectsRead = 0;
    }

    while (_rectsRead < _pendingRects) {
      // Each rect header: x(2) y(2) w(2) h(2) encoding(4) = 12 bytes
      if (_buf.length < 12) return;
      final rh = _take(12)!;
      final bd = ByteData.sublistView(rh);
      final x = bd.getUint16(0);
      final y = bd.getUint16(2);
      final w = bd.getUint16(4);
      final h = bd.getUint16(6);
      final enc = bd.getInt32(8);

      final consumed = _decodeRect(x, y, w, h, enc);
      if (!consumed) {
        // Put the rect header back and wait for more data
        final tmp = _buf.takeBytes();
        _buf.add(rh);
        _buf.add(tmp);
        return;
      }
      _rectsRead++;
    }

    // All rects consumed — emit updated frame and request next update
    _frameController.add(framebuffer);
    _sendFbUpdateRequest(incremental: true);
    _phase = _Phase.msgType;
    _process();
  }

  /// Returns true if the rectangle was fully consumed from the buffer.
  bool _decodeRect(int x, int y, int w, int h, int encoding) {
    switch (encoding) {
      case _encodingRaw:
        return _decodeRaw(x, y, w, h);
      case _encodingCopyRect:
        return _decodeCopyRect(x, y, w, h);
      case _encodingZlib:
        return _decoder.decodeZlib(_buf, x, y, w, h, framebuffer);
      case _encodingZrle:
        return _decoder.decodeZrle(_buf, x, y, w, h, framebuffer);
      default:
        // Unknown encoding — skip (treat as empty)
        return true;
    }
  }

  bool _decodeRaw(int x, int y, int w, int h) {
    final size = w * h * 4; // 32-bit pixels
    if (_buf.length < size) return false;
    final data = _take(size)!;
    var di = 0;
    for (var row = y; row < y + h; row++) {
      final base = (row * _fbWidth + x) * 4;
      for (var col = 0; col < w; col++) {
        // Server sends BGRA (since we requested BGR0 pixel format)
        framebuffer.pixels[base + col * 4] = data[di + 2]; // R
        framebuffer.pixels[base + col * 4 + 1] = data[di + 1]; // G
        framebuffer.pixels[base + col * 4 + 2] = data[di]; // B
        framebuffer.pixels[base + col * 4 + 3] = 0xff;
        di += 4;
      }
    }
    return true;
  }

  bool _decodeCopyRect(int x, int y, int w, int h) {
    if (_buf.length < 4) return false;
    final data = _take(4)!;
    final bd = ByteData.sublistView(data);
    final srcX = bd.getUint16(0);
    final srcY = bd.getUint16(2);
    framebuffer.copyPixels(x, y, w, h, srcX, srcY);
    return true;
  }

  // ── Client → Server messages ───────────────────────────────────────────────

  void _sendSetPixelFormat() {
    // Message type 0, 3 padding bytes, then PixelFormat (16 bytes)
    // Request 32bpp BGRA so raw tiles are easy to copy into the ARGB buffer
    final msg = Uint8List(20);
    msg[0] = 0; // SetPixelFormat
    // bytes-per-pixel=4, depth=24, big-endian=0, true-colour=1
    msg[4] = 32; // bits-per-pixel
    msg[5] = 24; // depth
    msg[6] = 0; // big-endian
    msg[7] = 1; // true-colour
    // R/G/B maxima
    final bd = ByteData.sublistView(msg);
    bd.setUint16(8, 255); // red-max
    bd.setUint16(10, 255); // green-max
    bd.setUint16(12, 255); // blue-max
    msg[14] = 16; // red-shift
    msg[15] = 8; // green-shift
    msg[16] = 0; // blue-shift
    _socket!.add(msg);
  }

  void _sendSetEncodings() {
    // Message type 2: SetEncodings
    const encs = [
      _encodingZrle,
      _encodingZlib,
      _encodingCopyRect,
      _encodingRaw,
    ];
    final msg = Uint8List(4 + encs.length * 4);
    msg[0] = 2; // SetEncodings
    final bd = ByteData.sublistView(msg);
    bd.setUint16(2, encs.length);
    for (var i = 0; i < encs.length; i++) {
      bd.setInt32(4 + i * 4, encs[i]);
    }
    _socket!.add(msg);
  }

  void _sendFbUpdateRequest({required bool incremental}) {
    final msg = Uint8List(10);
    msg[0] = 3; // FramebufferUpdateRequest
    msg[1] = incremental ? 1 : 0;
    final bd = ByteData.sublistView(msg);
    bd.setUint16(2, 0);
    bd.setUint16(4, 0);
    bd.setUint16(6, _fbWidth);
    bd.setUint16(8, _fbHeight);
    _socket!.add(msg);
  }

  // ── VNC DES auth ─────────────────────────────────────────────────────────

  Uint8List _desEncrypt(Uint8List challenge, String password) {
    // VNC uses reversed-bit-order DES with the password as the key (max 8 chars)
    final key = Uint8List(8);
    final pw = password.codeUnits;
    for (var i = 0; i < 8 && i < pw.length; i++) {
      key[i] = _reverseBits(pw[i]);
    }
    final result = Uint8List(16);
    result.setRange(0, 8, _desBlock(challenge.sublist(0, 8), key));
    result.setRange(8, 16, _desBlock(challenge.sublist(8, 16), key));
    return result;
  }

  int _reverseBits(int b) {
    var r = 0;
    for (var i = 0; i < 8; i++) {
      r = (r << 1) | (b & 1);
      b >>= 1;
    }
    return r;
  }

  // Single DES block encryption (ECB, 64-bit block, 64-bit key).
  // Implements the standard DES algorithm as required by RFB VNC auth.
  Uint8List _desBlock(Uint8List block, Uint8List key) {
    final subkeys = _generateSubkeys(key);
    var l = _bytesToInt(block.sublist(0, 4));
    var r = _bytesToInt(block.sublist(4, 8));

    // Initial permutation
    final ip = _permute64(_combineToInt64(l, r), _IP);
    l = (ip >> 32).toInt() & 0xffffffff;
    r = ip.toInt() & 0xffffffff;

    for (var i = 0; i < 16; i++) {
      final tmp = r;
      r = l ^ _feistel(r, subkeys[i]);
      l = tmp;
    }

    // Final permutation (inverse IP)
    final fp = _permute64(_combineToInt64(r, l), _FP);
    return _int64ToBytes(fp);
  }

  // Feistel function: expansion, XOR with subkey, S-box substitution, permutation
  int _feistel(int r, int subkey) {
    final expanded = _expand(r);
    final mixed = expanded ^ subkey;
    var result = 0;
    for (var i = 0; i < 8; i++) {
      final s6 = (mixed >> ((7 - i) * 6)) & 0x3f;
      final row = ((s6 >> 5) & 1) | ((s6 & 1) << 1);
      final col = (s6 >> 1) & 0xf;
      result = (result << 4) | _S[i][row * 16 + col];
    }
    return _permute32(result, _P);
  }

  int _expand(int r) {
    var result = 0;
    for (var i = 0; i < 48; i++) {
      final bit = _E[i] - 1;
      result = (result << 1) | ((r >> (31 - bit)) & 1);
    }
    return result;
  }

  int _permute64(int input, List<int> table) {
    var result = 0;
    for (var i = 0; i < table.length; i++) {
      final bit = table[i] - 1;
      result = (result << 1) | ((input >> (63 - bit)) & 1);
    }
    return result;
  }

  int _permute32(int input, List<int> table) {
    var result = 0;
    for (var i = 0; i < table.length; i++) {
      final bit = table[i] - 1;
      result = (result << 1) | ((input >> (31 - bit)) & 1);
    }
    return result;
  }

  List<int> _generateSubkeys(Uint8List key) {
    var c = 0;
    var d = 0;
    for (var i = 0; i < 28; i++) {
      final bit = _PC1C[i] - 1;
      c = (c << 1) | ((key[bit ~/ 8] >> (7 - bit % 8)) & 1);
    }
    for (var i = 0; i < 28; i++) {
      final bit = _PC1D[i] - 1;
      d = (d << 1) | ((key[bit ~/ 8] >> (7 - bit % 8)) & 1);
    }
    final subkeys = <int>[];
    for (var i = 0; i < 16; i++) {
      final shifts = _SHIFTS[i];
      c = _rotateLeft28(c, shifts);
      d = _rotateLeft28(d, shifts);
      var subkey = 0;
      final cd = (c << 28) | d;
      for (var j = 0; j < 48; j++) {
        final bit = _PC2[j] - 1;
        subkey = (subkey << 1) | ((cd >> (55 - bit)) & 1);
      }
      subkeys.add(subkey);
    }
    return subkeys;
  }

  int _rotateLeft28(int val, int n) {
    return ((val << n) | (val >> (28 - n))) & 0xfffffff;
  }

  int _bytesToInt(Uint8List b) =>
      (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3];

  int _combineToInt64(int high, int low) =>
      ((high & 0xffffffff) * 0x100000000) + (low & 0xffffffff);

  Uint8List _int64ToBytes(int v) {
    final b = Uint8List(8);
    for (var i = 7; i >= 0; i--) {
      b[i] = v & 0xff;
      v >>= 8;
    }
    return b;
  }

  // DES constants
  static const _IP = [
    58,50,42,34,26,18,10,2, 60,52,44,36,28,20,12,4,
    62,54,46,38,30,22,14,6, 64,56,48,40,32,24,16,8,
    57,49,41,33,25,17, 9,1, 59,51,43,35,27,19,11,3,
    61,53,45,37,29,21,13,5, 63,55,47,39,31,23,15,7,
  ];
  static const _FP = [
    40,8,48,16,56,24,64,32, 39,7,47,15,55,23,63,31,
    38,6,46,14,54,22,62,30, 37,5,45,13,53,21,61,29,
    36,4,44,12,52,20,60,28, 35,3,43,11,51,19,59,27,
    34,2,42,10,50,18,58,26, 33,1,41, 9,49,17,57,25,
  ];
  static const _E = [
    32,1,2,3,4,5, 4,5,6,7,8,9, 8,9,10,11,12,13,
    12,13,14,15,16,17, 16,17,18,19,20,21, 20,21,22,23,24,25,
    24,25,26,27,28,29, 28,29,30,31,32,1,
  ];
  static const _P = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,
                     2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25];
  static const _PC1C = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,
                        10,2,59,51,43,35,27,19,11,3,60,52,44,36];
  static const _PC1D = [63,55,47,39,31,23,15,7,62,54,46,38,30,22,
                        14,6,61,53,45,37,29,21,13,5,28,20,12,4];
  static const _PC2 = [14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,
                       26,8,16,7,27,20,13,2,41,52,31,37,47,55,30,40,
                       51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32];
  static const _SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1];
  static const _S = [
    [14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7,
      0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8,
      4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0,
     15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13],
    [15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10,
      3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5,
      0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15,
     13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9],
    [10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8,
     13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1,
     13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7,
      1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12],
    [ 7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15,
     13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9,
     10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4,
      3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14],
    [ 2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9,
     14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6,
      4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14,
     11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3],
    [12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11,
     10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8,
      9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6,
      4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13],
    [ 4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1,
     13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6,
      1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2,
      6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12],
    [13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7,
      1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2,
      7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8,
      2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11],
  ];

  void dispose() {
    _sub.cancel();
    _socket?.destroy();
    _frameController.close();
    _stateController.close();
  }
}

enum _Phase {
  version,
  security,
  vncAuth,
  securityResult,
  serverInit,
  msgType,
  fbUpdate,
}
