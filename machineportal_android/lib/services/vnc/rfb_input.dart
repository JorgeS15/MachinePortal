import 'dart:io';
import 'dart:typed_data';

/// Sends RFB client input events (pointer and key) to the VNC server.
class RfbInput {
  final Socket _socket;

  RfbInput(this._socket);

  /// Sends a pointer event. [buttons] is a bitmask: bit0=left, bit1=middle, bit2=right.
  void pointerEvent(int x, int y, {int buttons = 0}) {
    final msg = Uint8List(6);
    msg[0] = 5; // PointerEvent
    msg[1] = buttons;
    final bd = ByteData.sublistView(msg);
    bd.setUint16(2, x.clamp(0, 65535));
    bd.setUint16(4, y.clamp(0, 65535));
    _socket.add(msg);
  }

  /// Sends a left-click at [x],[y].
  void click(int x, int y) {
    pointerEvent(x, y, buttons: 1);
    pointerEvent(x, y, buttons: 0);
  }

  /// Sends a right-click at [x],[y].
  void rightClick(int x, int y) {
    pointerEvent(x, y, buttons: 4);
    pointerEvent(x, y, buttons: 0);
  }

  /// Scrolls up (wheel up = button 4) at [x],[y].
  void scrollUp(int x, int y) {
    pointerEvent(x, y, buttons: 8);
    pointerEvent(x, y, buttons: 0);
  }

  /// Scrolls down (wheel down = button 5) at [x],[y].
  void scrollDown(int x, int y) {
    pointerEvent(x, y, buttons: 16);
    pointerEvent(x, y, buttons: 0);
  }

  /// Sends a key event. [keysym] is an X11 keysym value.
  void keyEvent(int keysym, {required bool down}) {
    final msg = Uint8List(8);
    msg[0] = 4; // KeyEvent
    msg[1] = down ? 1 : 0;
    final bd = ByteData.sublistView(msg);
    bd.setUint32(4, keysym);
    _socket.add(msg);
  }

  /// Sends a Unicode character as a key press+release.
  void sendChar(int codePoint) {
    // For ASCII and Latin-1 (≤ 0xFF), keysym == codepoint
    // For others use Unicode keysym (0x01000000 + codepoint)
    final keysym = codePoint <= 0xff ? codePoint : 0x01000000 + codePoint;
    keyEvent(keysym, down: true);
    keyEvent(keysym, down: false);
  }

  /// Convenience: send a string one character at a time.
  void sendString(String s) {
    for (final rune in s.runes) {
      sendChar(rune);
    }
  }

  // Common X11 keysyms for special keys
  static const ksBackspace = 0xff08;
  static const ksTab = 0xff09;
  static const ksReturn = 0xff0d;
  static const ksEscape = 0xff1b;
  static const ksDelete = 0xffff;
  static const ksHome = 0xff50;
  static const ksLeft = 0xff51;
  static const ksUp = 0xff52;
  static const ksRight = 0xff53;
  static const ksDown = 0xff54;
  static const ksEnd = 0xff57;
  static const ksF1 = 0xffbe;
  static const ksCtrlL = 0xffe3;
  static const ksAltL = 0xffe9;
}
