# Machine Portal — User Instructions

A step-by-step guide to every task in Machine Portal. For a shorter overview see the
[README](README.md), or open **? Guide** inside the app for the same steps on screen.

---

## Contents
1. [Activating the app](#1-activating-the-app)
2. [Adding a machine](#2-adding-a-machine)
3. [Connecting to a machine](#3-connecting-to-a-machine)
4. [SSH tunnel machines](#4-ssh-tunnel-machines)
5. [Opening the machine folder](#5-opening-the-machine-folder)
6. [Searching and filtering](#6-searching-and-filtering)
7. [Editing and deleting machines](#7-editing-and-deleting-machines)
8. [Changing a card image](#8-changing-a-card-image)
9. [Settings](#9-settings)
10. [Backup and restore](#10-backup-and-restore)
11. [Updating the app](#11-updating-the-app)
12. [Getting help](#12-getting-help)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Activating the app

The first time you open Machine Portal, an **Activation** window appears.

1. You'll see your **Device ID** — a short code unique to this computer.
2. Click **Copy** and send the Device ID to Equipack.
3. When you receive your **license key**, paste it into the box and click **Activate**.

The license is stored on this PC and is tied to it. You don't need an internet connection to use
the app after activating. If you move to a new computer, you'll need a new key for that machine —
contact Equipack.

---

## 2. Adding a machine

1. Click **+ Add** in the top-right corner.
2. Fill in:
   - **Name** — how the machine appears on the dashboard (required).
   - **IP address** — the machine's address on your network (required).
   - **Serial Number** — the machine's serial (required; also used to open its folder).
   - **Notes** — anything you want to remember (optional).
3. If the machine needs a secure tunnel, tick **SSH tunnel** and enter the SSH **username** and
   **password** (see [SSH tunnel machines](#4-ssh-tunnel-machines)).
4. Click **Save**. The new card appears on the dashboard.

Each machine keeps its own settings independently.

---

## 3. Connecting to a machine

- **Double-click** a card, **or**
- Click a card to select it, then click **Connect** in the toolbar.

The remote screen opens in its own window. When you finish, simply close that window — Machine
Portal shuts the connection down and cleans up automatically.

The coloured dot on each card tells you if the machine is reachable before you try:
**green** = reachable, **red** = not reachable, **grey** = not checked yet.

---

## 4. SSH tunnel machines

Some machines are reached through a secure SSH tunnel. When **SSH tunnel** is enabled on a machine:

- Machine Portal opens the tunnel for you automatically when you connect — there's nothing extra
  to do each time.
- Enter the SSH **username** and **password** once, when adding or editing the machine.
- Passwords are shown as dots and are stored **encrypted** on your PC, never in plain text.

If a connection fails, double-check the IP address, username, and password. Your vendor can advise
which machines need SSH and what credentials to use.

---

## 5. Opening the machine folder

Machine Portal can open a machine's folder on a shared network drive, using its serial number.

1. In **Settings**, set the **Netdrive Path** to the base folder where machine folders live
   (for example a mapped drive or a `\\server\share` path).
2. Make sure the machine has a **Serial Number**.
3. Right-click the machine's card and choose **Open machine folder**.

The folder opens in Windows Explorer. If it doesn't open, check that the Netdrive Path is set and
that a folder for that serial number exists.

---

## 6. Searching and filtering

Use the **search bar** above the machine list to find machines quickly.

- Type any part of a **name**, **IP address**, or **serial number**.
- The list filters as you type.
- Clear the box to show all machines again.

---

## 7. Editing and deleting machines

**Edit:** right-click a card → **Edit** (or select it and use the toolbar). Change any detail and
click **Save**.

**Delete:** right-click a card → **Remove** (or select it and use the toolbar). You'll be asked to
confirm. Deleting a machine removes it from the dashboard only — it does nothing to the machine
itself.

---

## 8. Changing a card image

To make machines easier to recognise:

1. Right-click a card → **Change Image**.
2. Pick one of the built-in images or choose your own picture.
3. The card updates immediately.

---

## 9. Settings

Open **Settings** from the toolbar to adjust:

| Setting | What it does |
|---|---|
| **Theme** | Switch between Light and Dark appearance. |
| **Language** | English or Português (PT). |
| **Netdrive Path** | Base network path used by *Open machine folder*. |
| **VNC Port** | Port used for direct (non-tunnelled) connections. |
| **SSH Remote Port** | The VNC port on the remote side of the SSH tunnel. |
| **SSH Tunnel Wait** | How long to wait for the tunnel before opening the viewer. |
| **Backup / Restore** | Export or import your machine list (see below). |

---

## 10. Backup and restore

**Export (backup):**
1. In **Settings**, click **Export…**.
2. Choose where to save the `.json` file.

The backup contains your machines and settings. For security it **does not include SSH passwords**
— those are encrypted for this PC and cannot be read on another one.

**Import (restore):**
1. In **Settings**, click **Import…**.
2. Choose a backup `.json` file.
3. Confirm when asked. Your current list is replaced with the one from the backup.
4. Re-enter SSH passwords for any tunnelled machines (they aren't part of the backup).

---

## 11. Updating the app

Machine Portal checks for updates when it starts, and you can also check any time from **Settings**.

- When a newer version exists, you're offered the option to update.
- Downloads are **verified against Equipack's digital signature** before installing, so only genuine
  releases are ever run. If verification fails, the update is refused.
- After updating, the app restarts on the new version automatically.

---

## 12. Getting help

Click **? Help** in the toolbar to open the support form.

1. Type a short description of the problem.
2. Click **Send**. Your email program opens with the message ready, and the app's log file is
   attached automatically so support can see what happened.

Support: **Equipack, Lda.** — Jorge Santos — jorgesantos@equipack.pt

---

## 13. Troubleshooting

| Symptom | What to try |
|---|---|
| Status dot stays grey | The machine may be off/unreachable, or a firewall is blocking pings. |
| Connection fails | Check the IP address, that the machine is on, and (for SSH) the username/password. |
| "Local port already in use" | A previous session may still be open — close it, or restart Machine Portal. |
| *Open machine folder* does nothing | Set the Netdrive Path in Settings and make sure the machine has a serial number. |
| Activation dialog appears every launch | Re-activate; contact Equipack if you've lost your key. |

If a problem persists, use **? Help** to send a support request — the log is attached automatically.
