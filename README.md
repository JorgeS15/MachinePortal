# Machine Portal

**Remote access dashboard for your factory floor.**
Machine Portal is a single Windows application that lets you connect to, monitor, and
organise every machine on your network from one place — no installer, no technical setup.

<img width="952" height="715" alt="machine_portal_print" src="https://github.com/user-attachments/assets/a9420ab5-98e9-4360-912f-d604a0bace81" />

---

## What it does

Machine Portal keeps all your machines in one dashboard. Each machine is a card showing its
name, serial number, IP address, and a live status dot. Select a machine and click **Connect**
and the remote screen opens automatically — including setting up a secure SSH tunnel behind the
scenes when one is required. You can search your machines, open a machine's folder on a network
drive, keep notes, and back up your whole list to move it to another PC.

---

## Features

### Remote access
- **One-click connect** — select a machine and click **Connect**, or just double-click its card.
  The remote screen opens automatically and cleans itself up when you close it.
- **Secure SSH tunnel** — machines that need a tunnel are handled transparently. Credentials are
  never shown in plain text and are stored encrypted on your PC.
- **Live status** — every card shows a colour dot that refreshes every few seconds:
  **green** = reachable, **red** = not reachable, **grey** = not yet checked.

### Machine management
- **Add, edit, and remove** machines at any time.
- **Serial number and notes** on every machine, shown on the card and searchable.
- **Search bar** — filter instantly by name, IP address, or serial number.
- **Custom card image** — right-click a card → *Change Image* to make each machine easy to spot.
- **Right-click menu** on any card: Connect, Open machine folder, Change Image, Edit, Remove.

### Machine folder
- **Open machine folder** opens that machine's folder on your configured network drive
  (using its serial number), so documentation and files are one click away.

### Backup & restore
- **Export** your machine list and settings to a `.json` file, and **import** it on another PC or
  after a reinstall.
- For security, backups **do not include SSH passwords** (those are encrypted per-PC and can't be
  restored elsewhere) — you re-enter them once after restoring.

### Built-in help
- **? Guide** — a step-by-step how-to for every task, right inside the app.
- **? Help** — a support form that emails your message to Equipack with the log attached.

### Personalisation
- **Light and Dark** themes.
- **English and Portuguese (PT)** interface.

### Secure & licensed
- **Licensed per PC** — activate once with a key tied to this computer; no internet needed afterwards.
- **Encrypted credentials** — stored SSH passwords are protected with Windows account encryption.
- **Signed updates** — the app only installs updates that carry a valid signature from Equipack.

---

## System requirements

| | |
|---|---|
| Operating system | Windows 10 or Windows 11 (64-bit) |
| Network | Local network access to the machines you want to reach |
| Installation | None — a single `.exe`, no installer needed |

---

## Getting started

### 1. Activate the app
On first launch the **Activation** dialog shows your **Device ID** — a short code tied to this PC.
1. Click **Copy** to copy the Device ID.
2. Send it to your vendor (Equipack).
3. Paste the license key you receive and click **Activate**.

The license is saved locally; no internet connection is needed after activation.

### 2. Add your first machine
1. Click **+ Add** in the top-right.
2. Enter the **name**, **IP address**, and **serial number**.
3. Enable **SSH tunnel** if that machine needs one (your vendor will advise), and enter the SSH
   username/password.
4. Click **Save** — the card appears on the dashboard.

### 3. Connect
Click a card to select it and click **Connect**, or double-click the card.
The remote screen opens automatically. Close it when you're done — the connection cleans up by itself.

> New to the app? Open **? Guide** in the toolbar for the same steps with more detail, or read
> **[INSTRUCTIONS.md](INSTRUCTIONS.md)**.

---

## Everyday use

- **Find a machine** — type in the search bar (name, IP, or serial). The list filters as you type.
- **Open a machine's folder** — right-click the card → *Open machine folder* (requires the Netdrive
  Path set in Settings and a serial number on the machine).
- **Edit or remove** — right-click the card, or select it and use the toolbar.

---

## Settings

Open **Settings** to change:

| Setting | Description |
|---|---|
| Theme | Light or Dark |
| Language | English or Português (PT) |
| Netdrive Path | Base network path used by *Open machine folder* |
| VNC Port | Port used for direct (non-tunnelled) connections |
| SSH Remote Port | The VNC port on the remote side of the tunnel |
| SSH Tunnel Wait | How long to wait for the tunnel before opening the viewer |
| Backup / Restore | Export or import your machine list as a `.json` file |

---

## Updating

Machine Portal checks for new versions on startup. When one is available it offers to update;
the download is verified against Equipack's signature before it is installed, so only genuine
releases are ever run. You can also check manually in **Settings**.

---

## Troubleshooting

| Symptom | What to try |
|---|---|
| Status dot stays grey | The machine may be unreachable, or a firewall is blocking network pings |
| Connection fails | Check the IP address is correct, the machine is powered on, and (for SSH) the username/password |
| "Local port already in use" | A previous session may still be open — close it, or restart Machine Portal |
| Activation dialog appears every launch | Re-activate; contact your vendor if you've lost your license key |

If you can't resolve an issue, use **? Help** to send a support request — the log file is attached
automatically so support can diagnose it quickly.

---

## Support

**Equipack, Lda.** — Jorge Santos
jorgesantos@equipack.pt
