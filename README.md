# Machine Portal

A Windows desktop dashboard for managing remote VNC connections to Engel CC300 injection molding machine control panels, with SSH tunneling support, live ping monitoring, and hardware-bound offline licensing.

---

## Features

- **Multi-machine dashboard** — add, edit, and delete machines; each shown as a card with a live thumbnail
- **One-click connect** — SSH tunnel + VNC viewer launch handled automatically
- **Live ping monitor** — green/red dot per card shows reachability at a glance
- **Direct or SSH tunnel** — configurable per machine; older CC300 panels use direct VNC, newer ones require SSH
- **Light and Dark themes** — switchable in Settings
- **Backup & Restore** — export/import the machine list as JSON
- **Offline hardware licensing** — Ed25519-signed keys tied to the customer's machine; no internet required

---

## Installation (end users)

1. Obtain `MachinePortal.exe` from your vendor.
2. Run it — on first launch the **Activation** dialog appears.
3. Send the displayed **Device ID** to your vendor and paste the license key you receive.
4. The app opens; your config is stored in `%APPDATA%\MachinePortal\`.

> No installation required. The VNC viewer and PuTTY (plink) are bundled inside the exe.

---

## Adding a Machine

1. Click **+ Add Machine**.
2. Fill in:
   - **Name** — display label for the card
   - **IP Address** — machine IP on the network
   - **Use SSH tunnel** — enable for newer CC300 panels
   - SSH credentials and ports (only shown when SSH is enabled)
3. Click **Save**.

Click the card to connect. The ping dot updates every 5 seconds; the connection status indicator updates every 2 seconds.

---

## Settings

Open **Settings** (gear icon) to configure:

| Setting | Description |
|---|---|
| Theme | Light (lime green) or Dark (purple) |
| VNC Port | Port for direct VNC connections (default 5900) |
| SSH Remote Port | VNC port on the remote side of the tunnel (default 5900) |
| SSH Tunnel Wait | Seconds to wait for the tunnel before launching VNC (default 2) |
| Backup / Restore | Export or import the full machine list as a JSON file |

Changing the theme requires an app restart (prompted automatically).

---

## Licensing

### For customers

On first run, the app shows your **Device ID** — a 19-character code derived from your hardware (`XXXX-XXXX-XXXX-XXXX`). Send this to your vendor. Once you receive your license key, paste it into the activation dialog and click **Activate**. The key is saved locally; no internet is needed for future launches.

### For vendors (issuing keys)

**First-time setup** — generate your keypair once and keep `private.key` offline:

```
python tools/generate_keypair.py
```

This saves `tools/private.key` and prints the public key already embedded in
`dashboard/licensing.py`. Back up `private.key` securely — losing it means
existing keys still work but no new ones can be issued.

**Issuing a key** — use the CLI tool:

```
python tools/generate_license.py <DEVICE_ID> [YYYYMMDD|LIFETIME]
```

**Examples:**

```bash
# Lifetime license
python tools/generate_license.py A3F2-B1C9-4A8D-2C1E

# License valid until 31 Dec 2027
python tools/generate_license.py A3F2-B1C9-4A8D-2C1E 20271231
```

The tool prints the license key to send to the customer. Use the **Copy** button
in the activation dialog to get the Device ID without transcription errors.

> **Security:** Only the public key ships inside the app. Even if someone
> decompiles the binary, they cannot forge keys without `private.key`.

---

## Building from Source

### Prerequisites

| Tool | Notes |
|---|---|
| Python 3.11+ | Add to PATH |
| PyNaCl | `pip install PyNaCl` |
| `plink.exe` | From [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) |
| `vncviewer.exe` | Portable TigerVNC from [TigerVNC releases](https://github.com/TigerVNC/tigervnc/releases) — rename `vncviewer64-X.Y.Z.exe` to `vncviewer.exe` |

### Steps

1. Place `plink.exe` and `vncviewer.exe` in `engelrv_dashboard/assets/`.
2. Run `build.bat`.
3. The output is `dist\MachinePortal.exe`.

PyInstaller is installed automatically by the build script if not already present.

---

## Legacy Batch Script

`cc300_remoteview.bat` is the original single-machine script included for reference or for environments where the GUI is not needed. It prompts for an IP address and SSH preference, then launches the VNC viewer directly. See the script header for configuration options.

---

## Project Structure

```
dashboard/
  main.py          Entry point; license gate
  gui.py           Tkinter UI (dashboard, dialogs, themes)
  config.py        Machine and Settings data model; JSON persistence
  connection.py    SSH tunnel + VNC subprocess management; ping loop
  licensing.py     Hardware fingerprint, Ed25519 key verification
  version.py       Version string
  assets/          Bundled binaries and icon (not in source control)
  machineportal.spec  PyInstaller spec

tools/
  generate_keypair.py  One-time keypair generation (run once, keep private.key offline)
  generate_license.py  Vendor CLI for issuing license keys
  private.key          Ed25519 private key seed — never commit or share

build.bat          One-click build script (Windows)
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Activation dialog appears every launch | Ensure `license.key` exists in `%APPDATA%\MachinePortal\`; re-activate if missing |
| Ping dots stay gray | Firewall may block ICMP; dots turn green/red only if ping reaches the host |
| SSH tunnel fails to start | Check IP, username, and password; increase **SSH Tunnel Wait** in Settings |
| Direct connection fails | The CC300 panel likely requires an SSH tunnel — enable it on the machine card |
| Log file location | `%APPDATA%\MachinePortal\machineportal.log` |

---

## Author

**Jorge Santos** (JorgeS15)  
GitHub: [@JorgeS15](https://github.com/JorgeS15)

## Disclaimer

Unofficial tool. Not affiliated with Engel Austria GmbH.
