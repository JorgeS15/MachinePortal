# Machine Portal

**Remote access dashboard for your factory floor.**  
Machine Portal lets you connect to and monitor any machine on your network from a single Windows application — no technical setup required.

---

## Features

### Remote Access
- **One-click connect** — select a machine and click Connect (or double-click its card). The app handles everything in the background and launches the remote view automatically.
- **SSH tunnel support** — machines that require a secure tunnel are handled transparently; no manual configuration needed.
- **Live reachability monitor** — every machine card shows a colour dot that updates every few seconds: **green** means the machine is reachable, **red** means it is not.

### Dashboard Views
- **Grid View** — all your machines displayed as cards with name, IP address, connection type, and live status at a glance.
- **Shopfloor View** — a free-form canvas where you can arrange machine cards to match your physical factory floor layout.
  - Drag cards to any position and they stay there between sessions.
  - **Rotate** cards 90° at a time so the orientation matches how each machine sits on the floor.
  - **Scale** cards up or down so larger machines appear bigger than smaller ones.

### Machine Management
- Add, edit, and remove machines at any time.
- Right-click any card for quick access to Connect, Edit, and Remove.
- Each machine stores its own connection settings independently.

### Settings & Customisation
- **Light and Dark themes** — choose the appearance that works best in your environment.
- **English and Portuguese (PT)** interface languages.
- **Backup & Restore** — export your full machine list to a file and import it on another PC or after a reinstallation.

### Help & Support
- The **? Help** button in the toolbar opens a support form pre-filled with your contact details. Clicking Send opens your email client with a support message ready to go — the app's log file and configuration are attached automatically.

---

## System Requirements

| | |
|---|---|
| Operating system | Windows 10 or Windows 11 (64-bit) |
| Network | Local network access to the machines you want to monitor |
| Installation | None — single `.exe` file, no installer needed |

---

## Getting Started

### 1. Activate the app

On first launch the **Activation** dialog appears. It shows your **Device ID** — a short code tied to this PC.

1. Copy the Device ID using the **Copy** button.
2. Send it to your vendor (Equipack).
3. Paste the license key you receive and click **Activate**.

The license is saved locally. No internet connection is needed after activation.

### 2. Add your first machine

1. Click **+ Add** in the top-right corner.
2. Fill in the machine name and IP address.
3. Enable **SSH tunnel** if required for that machine (your vendor will advise).
4. Click **Save** — the card appears on the dashboard.

### 3. Connect

Click a card to select it, then click **Connect** in the toolbar — or just double-click the card directly.  
The remote view opens automatically. Close it when you are done; the connection cleans up by itself.

---

## Shopfloor View

Switch between Grid View and Shopfloor View using the button in the bottom toolbar.

In Shopfloor View you can:

- **Drag** any card to position it where that machine sits on your factory floor.
- **Right-click** a card for extra options:
  - **Rotate 90°** — rotate the card to match the machine's real-world orientation.
  - **Scale…** — resize the card to reflect how large or small the machine is relative to others.

Positions, rotations, and scales are saved automatically.

---

## Settings

Click **⚙ Settings** to change:

| Setting | Description |
|---|---|
| Theme | Light (green) or Dark (purple) |
| Language | English or Português (PT) |
| VNC Port | Port used for direct connections |
| SSH Remote Port | VNC port on the remote side of the tunnel |
| SSH Tunnel Wait | How long to wait for the tunnel before launching the viewer |
| Backup / Restore | Export or import your machine list as a `.json` file |

---

## Troubleshooting

| Symptom | What to try |
|---|---|
| Status dots stay grey | The machine may be unreachable or a firewall is blocking network pings |
| Connection fails | Verify the machine's IP address is correct and it is powered on |
| Activation dialog appears on every launch | Re-activate — contact your vendor if you have lost your license key |

If you cannot resolve an issue, use the **? Help** button to send a support request. The log file is attached automatically so the support team can diagnose the problem right away.

---

## Support

**Equipack**  
Jorge Santos — jorgesantos@equipack.pt
