# Changelog

All notable changes to Machine Portal are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.2.0] – 2026-05-12

### Changed
- **Ed25519 asymmetric signing** replaces HMAC-SHA256 for license key verification.
  The app now ships only an embedded public key; the private signing key stays
  offline with the vendor. Even after full binary decompilation (e.g. with
  `pyinstxtractor`), an attacker cannot forge valid keys.
  **Old 0.1.x HMAC keys are not compatible — existing licenses must be reissued.**

### Added
- **`tools/generate_keypair.py`** — one-time tool to generate a fresh Ed25519
  keypair and save `tools/private.key`. Run this once; keep `private.key` offline.
- **Copy button** next to the Device ID in the activation dialog — eliminates
  manual transcription and the 0/O visual confusion that caused key generation
  to fail.

### Fixed
- **First-launch crash** — `ActivationDialog._build` passed `pady` twice to
  `.pack()`, raising `TypeError: got multiple values for keyword argument 'pady'`.
- **Machine fingerprint non-determinism** — `get_machine_fingerprint()` result
  is now cached per process, preventing hash mismatches if WMIC or `uuid.getnode()`
  returned different values between showing the Device ID and verifying the key.
- **O vs 0 typo in device IDs** — `generate_key` now substitutes letter O → digit 0
  before processing, since the Courier New bold font makes them visually identical.

### Requires
- `pip install PyNaCl` in both the app environment and the vendor tools environment.

---

## [0.1.7] – 2026-05-12

### Added
- **Offline hardware licensing** — on first run, the app shows an activation dialog
  with a Device ID derived from Windows Machine GUID, motherboard serial, and MAC
  address. The vendor generates a signed license key via `tools/generate_license.py`;
  the key is verified locally with HMAC-SHA256 (no internet required).
  Keys support a `LIFETIME` expiry or a fixed date (`YYYYMMDD`).
  The activated license is stored in `%APPDATA%\MachinePortal\license.key`.

---

## [0.1.6] – 2026-05-12

### Changed
- **App renamed** from "EngelRV" to **"Machine Portal"** — window title, title bar,
  config directory (`%APPDATA%\MachinePortal\`), log file, backup filename, exe name,
  and all build script references updated.
- **Lime green Light theme** — Light theme accent color changed from dark green to
  lime green (`#72b81a`), with matching card thumbnails, separators, and entry borders.
- **Log file moved** to `%APPDATA%\MachinePortal\machineportal.log` (same folder as
  `machines.json`), replacing the previous location next to the `.exe` which could be
  read-only on some systems.

---

## [0.1.5] – 2026-05-12

### Added
- **Theme support** – Light (default, green accent) and Dark (purple accent) themes,
  selectable in the Settings dialog under a new **Theme** section.
  The app restarts automatically when the theme changes to apply it fully.
- **Light theme** – clean white/green palette designed for daytime use; replaces the
  previous dark-only UI as the shipping default.
- **Updated icons** – embedded PNG icon and app `.ico` updated to match the Light
  (green) theme; the Dark theme shows the original purple icon as the fallback.

### Changed
- All colour constants are now driven by `set_theme()`, making the entire GUI
  (cards, dialogs, buttons, separators, entries) fully theme-aware.
- Secondary buttons (Cancel, Export, Import, Edit, Settings) now use the
  theme's `BTN_SEC` colour instead of a hardcoded dark value.

---

## [0.1.4] – 2026-05-12

### Added
- **Right-click context menu** on machine cards — right-clicking any card
  selects it and shows a small dropdown with **Connect**, **Edit**, and
  **Remove** actions, styled to match the dark theme.

---

## [0.1.3] – 2026-05-12

### Fixed
- **Ping console flash** – `ping` subprocess now runs with
  `CREATE_NO_WINDOW` on Windows; no cmd window ever appears.
- **Exe icon not showing** – replaced PNG-only ICO (ignored by Windows
  Explorer/taskbar) with a proper multi-size ICO containing BMP entries
  at 16×16, 32×32, 48×48 plus a PNG entry at 256×256.
- **Stale build cache** – added `--clean` to `build.bat` so PyInstaller
  always picks up fresh assets on every build.

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
