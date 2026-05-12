# Changelog

All notable changes to EngelRV are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.1.2] – 2026-05-12

### Added
- **Ping monitor** – a background thread pings every configured machine every 5 s.
  The status dot on each card updates every 2 s: green = reachable, red = unreachable,
  grey = not yet polled.
- **Backup & Restore** – Export and Import buttons in the Settings dialog let you
  save/load the full config (machines + settings) as a portable `.json` file.

### Fixed
- **App icon not appearing in built `.exe`** – switched from `iconphoto()` (PNG only)
  to `wm_iconbitmap()` with the bundled `engelrv.ico`, which correctly sets both the
  title-bar and taskbar icon on Windows. Falls back to embedded base64 PNG in dev mode.

---

## [0.1.1] – 2026-05-12

### Added
- **Grid card view** – machines are now displayed as RealVNC-style cards with a
  monitor thumbnail, status dot, IP address, and connection-type badge
  (SSH+VNC / Direct VNC). Double-click a card to connect.
- **Settings dialog** – ⚙ Settings button exposes: starting SSH port,
  remote VNC port, direct VNC port, tunnel wait time, and default SSH credentials.
- **Per-machine SSH port** – each machine stores its own local-forwarding port
  (auto-assigned from the configured starting port: 10062, 10063, …).
- **App icon** – window title-bar and taskbar icon (purple monitor logo).
- **Version label** – `v0.1.1` shown in the bottom-right corner of the main window.
- **File logging** – all connection errors are written to `engelrv.log` next to
  the executable, including full stack traces.
- **Empty state** – a friendly message is shown when no machines have been added.

### Fixed
- **[WinError 2] on connect** – PyInstaller bundle was looking for `vncviewer.exe`
  and `plink.exe` at the wrong path (`_MEIPASS\file` instead of
  `_MEIPASS\assets\file`). Connection now works correctly from the compiled `.exe`.

### Changed
- `Settings.ssh_local_port` replaced by `Settings.ssh_port_start` (per-machine
  ports). Existing config files load cleanly — unknown keys are silently ignored.

---

## [0.1.0] – 2026-05-01

### Added
- Initial release.
- List view dashboard showing machine name, IP address, and connection type.
- Add / Edit / Delete machines with SSH tunnel or direct VNC options.
- SSH tunnel via bundled `plink.exe`; VNC viewer via bundled `vncviewer.exe`.
- Config persisted to `%APPDATA%\EngelRV\machines.json`.
- Single-file PyInstaller build (`engelrv.spec`).
