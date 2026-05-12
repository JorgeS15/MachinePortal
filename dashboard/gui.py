import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

import config
import connection
from config import Machine, Settings
from version import VERSION


def _asset_path(filename: str) -> str:
    if getattr(sys, "frozen", False):
        base = os.path.join(sys._MEIPASS, "assets")  # type: ignore[attr-defined]
    else:
        base = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(base, filename)


# ── Embedded icons (64×64 RGBA PNG, base64) ───────────────────────────────────
_ICON_LIGHT_B64 = (
    "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"
)

_ICON_DARK_B64 = (
    "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"
)

# ── Theme definitions ─────────────────────────────────────────────────────────
THEMES: dict[str, dict] = {
    "Light": {
        "BG":              "#f7f8f2",
        "SURFACE":         "#eaefd8",
        "CARD_BG":         "#ffffff",
        "ACCENT":          "#72b81a",
        "ACCENT_H":        "#85d020",
        "BTN_SEC":         "#7a9470",
        "TEAL":            "#1b8a7e",
        "TEXT":            "#1e2a12",
        "TEXT_DIM":        "#4a6030",
        "TEXT_TINY":       "#8aaa72",
        "GREEN":           "#4caf50",
        "RED":             "#e53935",
        "SEP_COLOR":       "#d0dab8",
        "ENTRY_BG":        "#ffffff",
        "ENTRY_BORDER":    "#a8c870",
        "THUMB_BG":        "#eef5d8",
        "MONITOR_OUTLINE": "#72b81a",
        "MONITOR_FILL":    "#dff0b0",
        "MONITOR_STAND":   "#72b81a",
        "MONITOR_TEXT":    "#4a7a0e",
        "ICON_B64":        _ICON_LIGHT_B64,
    },
    "Dark": {
        "BG":              "#1e1e2e",
        "SURFACE":         "#2a2a3e",
        "CARD_BG":         "#252538",
        "ACCENT":          "#7c6af7",
        "ACCENT_H":        "#9d8fff",
        "BTN_SEC":         "#44446a",
        "TEAL":            "#2a8a7f",
        "TEXT":            "#e0e0f0",
        "TEXT_DIM":        "#888aaa",
        "TEXT_TINY":       "#555575",
        "GREEN":           "#4caf83",
        "RED":             "#e05c5c",
        "SEP_COLOR":       "#2e2e48",
        "ENTRY_BG":        "#2a2a3e",
        "ENTRY_BORDER":    "#44446a",
        "THUMB_BG":        "#191928",
        "MONITOR_OUTLINE": "#4a4875",
        "MONITOR_FILL":    "#23233a",
        "MONITOR_STAND":   "#4a4875",
        "MONITOR_TEXT":    "#5a5a98",
        "ICON_B64":        _ICON_DARK_B64,
    },
}

# ── Active theme globals (Light defaults) ─────────────────────────────────────
_T = THEMES["Light"]
BG              = _T["BG"]
SURFACE         = _T["SURFACE"]
CARD_BG         = _T["CARD_BG"]
ACCENT          = _T["ACCENT"]
ACCENT_H        = _T["ACCENT_H"]
BTN_SEC         = _T["BTN_SEC"]
TEAL            = _T["TEAL"]
TEXT            = _T["TEXT"]
TEXT_DIM        = _T["TEXT_DIM"]
TEXT_TINY       = _T["TEXT_TINY"]
GREEN           = _T["GREEN"]
RED             = _T["RED"]
SEP_COLOR       = _T["SEP_COLOR"]
ENTRY_BG        = _T["ENTRY_BG"]
ENTRY_BORDER    = _T["ENTRY_BORDER"]
THUMB_BG        = _T["THUMB_BG"]
MONITOR_OUTLINE = _T["MONITOR_OUTLINE"]
MONITOR_FILL    = _T["MONITOR_FILL"]
MONITOR_STAND   = _T["MONITOR_STAND"]
MONITOR_TEXT    = _T["MONITOR_TEXT"]
_ICON_B64       = _T["ICON_B64"]
del _T

FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_SMALL = ("Segoe UI", 8)
FONT_CARD  = ("Segoe UI", 9)
FONT_TINY  = ("Segoe UI", 7)

CARD_W   = 172
CARD_H   = 164
THUMB_H  = 106
CARD_GAP = 14


def set_theme(name: str) -> None:
    global BG, SURFACE, CARD_BG, ACCENT, ACCENT_H, BTN_SEC, TEAL
    global TEXT, TEXT_DIM, TEXT_TINY, GREEN, RED, SEP_COLOR
    global ENTRY_BG, ENTRY_BORDER
    global THUMB_BG, MONITOR_OUTLINE, MONITOR_FILL, MONITOR_STAND, MONITOR_TEXT
    global _ICON_B64
    t = THEMES.get(name, THEMES["Light"])
    BG              = t["BG"]
    SURFACE         = t["SURFACE"]
    CARD_BG         = t["CARD_BG"]
    ACCENT          = t["ACCENT"]
    ACCENT_H        = t["ACCENT_H"]
    BTN_SEC         = t["BTN_SEC"]
    TEAL            = t["TEAL"]
    TEXT            = t["TEXT"]
    TEXT_DIM        = t["TEXT_DIM"]
    TEXT_TINY       = t["TEXT_TINY"]
    GREEN           = t["GREEN"]
    RED             = t["RED"]
    SEP_COLOR       = t["SEP_COLOR"]
    ENTRY_BG        = t["ENTRY_BG"]
    ENTRY_BORDER    = t["ENTRY_BORDER"]
    THUMB_BG        = t["THUMB_BG"]
    MONITOR_OUTLINE = t["MONITOR_OUTLINE"]
    MONITOR_FILL    = t["MONITOR_FILL"]
    MONITOR_STAND   = t["MONITOR_STAND"]
    MONITOR_TEXT    = t["MONITOR_TEXT"]
    _ICON_B64       = t["ICON_B64"]


def _style_entry(w) -> None:
    w.configure(
        bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
        relief="flat", highlightthickness=1,
        highlightbackground=ENTRY_BORDER, highlightcolor=ACCENT,
        font=FONT,
    )


def _btn(parent, text, cmd, bg=None, fg="white", width=12):
    _bg    = ACCENT if bg is None else bg
    _hover = ACCENT_H if bg is None else bg
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=_bg, fg=fg, activebackground=_hover, activeforeground=fg,
        relief="flat", font=FONT_BOLD, padx=8, pady=4, width=width, cursor="hand2",
    )
    b.bind("<Enter>", lambda e: b.configure(bg=_hover))
    b.bind("<Leave>", lambda e: b.configure(bg=_bg))
    return b


def _separator(parent) -> None:
    tk.Frame(parent, bg=SEP_COLOR, height=1).pack(fill="x")


# ── Machine card ──────────────────────────────────────────────────────────────
class MachineCard(tk.Frame):

    def __init__(self, parent, machine: Machine, on_select, on_double,
                 on_connect, on_edit, on_remove):
        super().__init__(
            parent,
            width=CARD_W, height=CARD_H,
            bg=CARD_BG,
            cursor="hand2",
            highlightthickness=2,
            highlightbackground=CARD_BG,
        )
        self.pack_propagate(False)
        self.machine     = machine
        self._on_select  = on_select
        self._on_double  = on_double
        self._on_connect = on_connect
        self._on_edit    = on_edit
        self._on_remove  = on_remove
        self._selected   = False

        self._thumb = tk.Canvas(
            self, width=CARD_W - 4, height=THUMB_H,
            bg=THUMB_BG, highlightthickness=0,
        )
        self._thumb.pack(fill="x")
        self._draw_thumb()

        info = tk.Frame(self, bg=CARD_BG)
        info.pack(fill="x", padx=8, pady=(6, 4))

        ping = connection.get_ping_state(machine.id)
        dot_color = GREEN if ping is True else (RED if ping is False else TEXT_DIM)
        self._dot = tk.Label(info, text="●", bg=CARD_BG, fg=dot_color, font=FONT_SMALL)
        self._dot.pack(side="left")
        tk.Label(info, text=machine.name, bg=CARD_BG, fg=TEXT,
                 font=FONT_CARD, anchor="w").pack(side="left", padx=(3, 0))

        meta = tk.Frame(self, bg=CARD_BG)
        meta.pack(fill="x", padx=8, pady=(0, 6))

        tk.Label(meta, text=machine.ip, bg=CARD_BG, fg=TEXT_DIM,
                 font=FONT_TINY, anchor="w").pack(side="left")

        badge_bg  = ACCENT if machine.ssh else TEAL
        badge_txt = "SSH+VNC" if machine.ssh else "Direct VNC"
        tk.Label(meta, text=badge_txt, bg=badge_bg, fg="white",
                 font=FONT_TINY, padx=4, pady=1).pack(side="right")

        self._bind_tree(self)

    def _draw_thumb(self):
        c = self._thumb
        w, h = CARD_W - 4, THUMB_H
        sx, sy = int(w * .13), int(h * .10)
        sw, sh = int(w * .74), int(h * .64)
        c.create_rectangle(sx + 2, sy + 2, sx + sw - 2, sy + sh - 2,
                           fill=MONITOR_FILL, outline="")
        c.create_rectangle(sx, sy, sx + sw, sy + sh,
                           outline=MONITOR_OUTLINE, fill="", width=2)
        mx = w // 2
        c.create_line(mx, sy + sh, mx, sy + sh + int(h * .14),
                      fill=MONITOR_STAND, width=3)
        bw = int(sw * .36)
        by = sy + sh + int(h * .14)
        c.create_rectangle(mx - bw, by, mx + bw, by + int(h * .10),
                           fill=MONITOR_STAND, outline="")
        parts    = self.machine.name.split()
        initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()
        c.create_text(w / 2, sy + sh / 2,
                      text=initials, fill=MONITOR_TEXT,
                      font=("Segoe UI", 17, "bold"))

    def _bind_tree(self, widget):
        widget.bind("<Button-1>",        lambda e: self._on_select(self.machine.id))
        widget.bind("<Double-Button-1>", lambda e: self._on_double(self.machine.id))
        widget.bind("<Button-3>",        self._show_context_menu)
        widget.bind("<Enter>",           self._on_hover_in)
        widget.bind("<Leave>",           self._on_hover_out)
        for child in widget.winfo_children():
            self._bind_tree(child)

    def _show_context_menu(self, event):
        self._on_select(self.machine.id)
        menu = tk.Menu(self, tearoff=0,
                       bg=SURFACE, fg=TEXT, activebackground=ACCENT,
                       activeforeground="white", relief="flat", font=FONT, bd=0)
        menu.add_command(label="Connect",
                         command=lambda: self._on_connect(self.machine.id))
        menu.add_separator()
        menu.add_command(label="Edit",
                         command=lambda: self._on_edit(self.machine.id))
        menu.add_command(label="Remove", foreground=RED, activeforeground=RED,
                         command=lambda: self._on_remove(self.machine.id))
        menu.tk_popup(event.x_root, event.y_root)

    def _on_hover_in(self, _e):
        if not self._selected and not connection.is_connected(self.machine.id):
            self.configure(highlightbackground=ENTRY_BORDER)

    def _on_hover_out(self, _e):
        if not self._selected and not connection.is_connected(self.machine.id):
            self.configure(highlightbackground=CARD_BG)

    def refresh_status(self):
        state  = connection.get_ping_state(self.machine.id)
        colour = GREEN if state is True else (RED if state is False else TEXT_DIM)
        self._dot.configure(fg=colour)

    def set_selected(self, selected: bool):
        self._selected = selected
        connected = connection.is_connected(self.machine.id)
        if selected:
            self.configure(highlightbackground=ACCENT)
        elif connected:
            self.configure(highlightbackground=GREEN)
        else:
            self.configure(highlightbackground=CARD_BG)


# ── Activation dialog ─────────────────────────────────────────────────────────
class ActivationDialog(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Machine Portal — Activation")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.activated = False
        self._build()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build(self):
        import licensing
        p = dict(padx=24, pady=6)

        tk.Label(self, text="Machine Portal", bg=BG, fg=ACCENT,
                 font=FONT_TITLE).pack(padx=24, pady=(18, 2))
        tk.Label(self, text="This copy is not activated.", bg=BG, fg=TEXT,
                 font=FONT).pack(padx=24, pady=(0, 8))

        # Device ID box
        box = tk.Frame(self, bg=SURFACE, padx=14, pady=10)
        box.pack(padx=24, pady=4, fill="x")
        tk.Label(box, text="Your Device ID", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w")
        tk.Label(box, text=licensing.get_display_id(), bg=SURFACE, fg=TEXT,
                 font=("Courier New", 14, "bold")).pack(anchor="w", pady=(3, 0))
        tk.Label(box, text="Send this ID to your vendor to receive a license key.",
                 bg=SURFACE, fg=TEXT_TINY, font=FONT_SMALL).pack(anchor="w", pady=(5, 0))

        # Key entry
        tk.Label(self, text="License Key:", bg=BG, fg=TEXT,
                 font=FONT).pack(padx=24, pady=(12, 2), anchor="w")
        self._key_var = tk.StringVar()
        tk.Entry(
            self, textvariable=self._key_var, width=38,
            bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
            relief="flat", highlightthickness=1,
            highlightbackground=ENTRY_BORDER, highlightcolor=ACCENT,
            font=("Courier New", 10),
        ).pack(padx=24, fill="x")
        self._msg = tk.Label(self, text="", bg=BG, fg=RED, font=FONT_SMALL)
        self._msg.pack(padx=24, anchor="w", pady=(3, 0))

        # Buttons
        bf = tk.Frame(self, bg=BG)
        bf.pack(padx=24, pady=(10, 18), fill="x")
        _btn(bf, "Exit", self._on_exit, bg=BTN_SEC, width=8).pack(side="left")
        _btn(bf, "Activate", self._on_activate, width=12).pack(side="right")

    def _on_activate(self):
        import licensing
        key = self._key_var.get().strip()
        if not key:
            self._msg.configure(text="Please enter a license key.")
            return
        valid, msg = licensing.verify_key(key)
        if not valid:
            self._msg.configure(text=msg)
            return
        licensing.save_license(key)
        self.activated = True
        self.destroy()

    def _on_exit(self):
        self.destroy()


# ── Add / Edit dialog ─────────────────────────────────────────────────────────
class MachineDialog(tk.Toplevel):

    def __init__(self, parent, machine: Machine | None = None,
                 settings: Settings | None = None, next_port: int = 10062):
        super().__init__(parent)
        self.result: Machine | None = None
        self._machine  = machine
        self._settings = settings or Settings()

        self.title("Edit Machine" if machine else "Add Machine")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        pad = {"padx": 14, "pady": 6}

        def lbl(text):
            return tk.Label(self, text=text, bg=BG, fg=TEXT_DIM, font=FONT, anchor="w")

        lbl("Machine Name").grid(row=0, column=0, sticky="w", **pad)
        self._name = tk.Entry(self, width=28)
        _style_entry(self._name)
        self._name.grid(row=0, column=1, **pad)

        lbl("IP Address").grid(row=1, column=0, sticky="w", **pad)
        self._ip = tk.Entry(self, width=28)
        _style_entry(self._ip)
        self._ip.grid(row=1, column=1, **pad)

        self._ssh_var = tk.BooleanVar(value=machine.ssh if machine else False)
        tk.Checkbutton(
            self, text="Requires SSH tunnel", variable=self._ssh_var,
            command=self._toggle_ssh,
            bg=BG, fg=TEXT, selectcolor=SURFACE,
            activebackground=BG, activeforeground=TEXT, font=FONT,
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=14, pady=8)

        self._user_lbl = lbl("SSH Username")
        self._user_lbl.grid(row=3, column=0, sticky="w", **pad)
        self._user = tk.Entry(self, width=28)
        _style_entry(self._user)
        self._user.grid(row=3, column=1, **pad)

        self._pass_lbl = lbl("SSH Password")
        self._pass_lbl.grid(row=4, column=0, sticky="w", **pad)
        self._password = tk.Entry(self, width=28, show="•")
        _style_entry(self._password)
        self._password.grid(row=4, column=1, **pad)

        self._port_lbl = lbl("SSH local port")
        self._port_lbl.grid(row=5, column=0, sticky="w", **pad)
        self._port = tk.Entry(self, width=28)
        _style_entry(self._port)
        self._port.grid(row=5, column=1, **pad)

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=14)
        _btn(btn_frame, "Save", self._save, width=10).pack(side="left", padx=6)
        _btn(btn_frame, "Cancel", self.destroy, bg=BTN_SEC, width=10).pack(side="left", padx=6)

        if machine:
            self._name.insert(0, machine.name)
            self._ip.insert(0, machine.ip)
            self._user.insert(0, machine.ssh_user)
            self._password.insert(0, machine.ssh_password)
            self._port.insert(0, str(machine.port))
        else:
            self._port.insert(0, str(next_port))
            if self._settings.default_ssh_user:
                self._user.insert(0, self._settings.default_ssh_user)
            if self._settings.default_ssh_password:
                self._password.insert(0, self._settings.default_ssh_password)

        self._toggle_ssh()
        self._name.focus_set()
        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())
        self._center(parent)

    def _center(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _toggle_ssh(self):
        ssh   = self._ssh_var.get()
        state = "normal" if ssh else "disabled"
        dim   = TEXT if ssh else TEXT_TINY
        for w in (self._user, self._password, self._port):
            w.configure(state=state)
        for lbl in (self._user_lbl, self._pass_lbl, self._port_lbl):
            lbl.configure(fg=dim)

    def _save(self):
        name = self._name.get().strip()
        ip   = self._ip.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Machine name is required.", parent=self)
            return
        if not ip:
            messagebox.showwarning("Validation", "IP address is required.", parent=self)
            return
        try:
            port = int(self._port.get().strip())
        except ValueError:
            messagebox.showwarning("Validation", "SSH local port must be an integer.", parent=self)
            return
        self.result = Machine(
            name=name, ip=ip,
            ssh=self._ssh_var.get(),
            ssh_user=self._user.get().strip() or "user",
            ssh_password=self._password.get(),
            port=port,
            id=self._machine.id if self._machine else __import__("uuid").uuid4().__str__(),
        )
        self.destroy()


# ── Settings dialog ───────────────────────────────────────────────────────────
class SettingsDialog(tk.Toplevel):

    def __init__(self, parent, settings: Settings,
                 on_export=None, on_import=None):
        super().__init__(parent)
        self.result: Settings | None = None

        self.title("Settings")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        pad  = {"padx": 14, "pady": 5}
        row  = [0]

        def section(title):
            tk.Label(
                self, text=title, bg=BG, fg=ACCENT, font=FONT_BOLD,
            ).grid(row=row[0], column=0, columnspan=2, sticky="w",
                   padx=14, pady=(14 if row[0] == 0 else 10, 2))
            row[0] += 1

        def field(label, default, show=None):
            tk.Label(self, text=label, bg=BG, fg=TEXT_DIM, font=FONT,
                     anchor="w").grid(row=row[0], column=0, sticky="w", **pad)
            e = tk.Entry(self, width=22, show=show)
            _style_entry(e)
            e.insert(0, str(default))
            e.grid(row=row[0], column=1, **pad)
            row[0] += 1
            return e

        section("SSH / Tunnel")
        self._port_start  = field("Starting SSH port",  settings.ssh_port_start)
        self._remote_port = field("Remote VNC port",    settings.ssh_remote_port)
        self._wait        = field("Tunnel wait (sec)",  settings.tunnel_wait_seconds)

        section("Direct VNC")
        self._vnc_port = field("VNC port", settings.vnc_port)

        section("Default Credentials")
        self._def_user = field("Default SSH user",     settings.default_ssh_user)
        self._def_pass = field("Default SSH password", settings.default_ssh_password, show="•")

        section("Theme")
        self._theme_var = tk.StringVar(value=settings.theme)
        tf = tk.Frame(self, bg=BG)
        tf.grid(row=row[0], column=0, columnspan=2, padx=14, pady=5, sticky="w")
        for t in ("Light", "Dark"):
            tk.Radiobutton(
                tf, text=t, variable=self._theme_var, value=t,
                bg=BG, fg=TEXT, selectcolor=SURFACE,
                activebackground=BG, activeforeground=TEXT, font=FONT,
            ).pack(side="left", padx=(0, 16))
        row[0] += 1

        section("Backup & Restore")
        br = tk.Frame(self, bg=BG)
        br.grid(row=row[0], column=0, columnspan=2, padx=14, pady=5, sticky="w")
        _btn(br, "Export…", on_export or (lambda: None), bg=BTN_SEC, width=10).pack(side="left", padx=(0, 8))
        _btn(br, "Import…", on_import or (lambda: None), bg=BTN_SEC, width=10).pack(side="left")
        row[0] += 1

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.grid(row=row[0], column=0, columnspan=2, pady=14)
        _btn(btn_frame, "Save",   self._save,    width=10).pack(side="left", padx=6)
        _btn(btn_frame, "Cancel", self.destroy,  bg=BTN_SEC, width=10).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())
        self._center(parent)

    def _center(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _save(self):
        try:
            self.result = Settings(
                ssh_port_start=int(self._port_start.get()),
                ssh_remote_port=int(self._remote_port.get()),
                vnc_port=int(self._vnc_port.get()),
                tunnel_wait_seconds=int(self._wait.get()),
                default_ssh_user=self._def_user.get().strip(),
                default_ssh_password=self._def_pass.get(),
                theme=self._theme_var.get(),
            )
            self.destroy()
        except ValueError:
            messagebox.showwarning(
                "Validation", "Port and wait values must be integers.", parent=self)


# ── Main window ───────────────────────────────────────────────────────────────
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.restart_requested = False

        self._machines, self._settings = config.load()
        set_theme(self._settings.theme)

        self.title("Machine Portal — Remote View Dashboard")
        self.geometry("760x540")
        self.minsize(580, 400)
        self.configure(bg=BG)

        try:
            ico = _asset_path("machineportal.ico")
            if os.path.exists(ico):
                self.wm_iconbitmap(ico)
            else:
                raise FileNotFoundError
        except Exception:
            try:
                self.iconphoto(True, tk.PhotoImage(data=_ICON_B64))
            except Exception:
                pass

        self._cards: dict[str, MachineCard] = {}
        self._selected_id: str | None = None

        self._build_ui()
        self._refresh_list()
        self.after(120, self._reflow_cards)

        connection.start_ping_loop(lambda: self._machines)
        self.after(2000, self._poll_status)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        title_frame = tk.Frame(self, bg=BG)
        title_frame.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(title_frame, text="Machine Portal", bg=BG, fg=ACCENT,
                 font=FONT_TITLE).pack(side="left")
        tk.Label(title_frame, text="Remote View Dashboard", bg=BG, fg=TEXT_DIM,
                 font=FONT).pack(side="left", padx=(8, 0), pady=2)
        _btn(title_frame, "+ Add", self._add_machine, width=8).pack(side="right")

        _separator(self)

        grid_container = tk.Frame(self, bg=BG)
        grid_container.pack(fill="both", expand=True, padx=16, pady=(10, 4))

        self._canvas = tk.Canvas(grid_container, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(grid_container, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._grid_frame = tk.Frame(self._canvas, bg=BG)
        self._canvas_win = self._canvas.create_window(
            (CARD_GAP, CARD_GAP), window=self._grid_frame, anchor="nw")

        self._grid_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self._canvas.bind(seq, self._on_scroll)

        _separator(self)

        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", padx=16, pady=(8, 6))

        self._btn_connect = _btn(toolbar, "Connect", self._connect, width=10)
        self._btn_connect.pack(side="left", padx=(0, 6))
        self._btn_edit = _btn(toolbar, "Edit", self._edit_machine, bg=BTN_SEC, width=8)
        self._btn_edit.pack(side="left", padx=(0, 6))
        self._btn_delete = _btn(toolbar, "Delete", self._delete_machine, bg=RED, width=8)
        self._btn_delete.pack(side="left")

        _btn(toolbar, "⚙  Settings", self._open_settings,
             bg=BTN_SEC, width=11).pack(side="right")

        self._status_lbl = tk.Label(toolbar, text="", bg=BG, fg=TEXT_DIM, font=FONT)
        self._status_lbl.pack(side="right", padx=(0, 10))

        tk.Label(self, text=f"v{VERSION}", bg=BG, fg=TEXT_TINY,
                 font=("Segoe UI", 8)).pack(side="bottom", anchor="e", padx=10, pady=(0, 4))

        self._update_buttons()

    # ── Grid helpers ──────────────────────────────────────────────────────────
    def _on_canvas_resize(self, e):
        self._canvas.itemconfig(self._canvas_win, width=max(1, e.width - CARD_GAP))
        self._reflow_cards()

    def _reflow_cards(self):
        w = self._canvas.winfo_width()
        if w <= 1:
            return
        cols = max(1, (w - CARD_GAP) // (CARD_W + CARD_GAP))
        for i, card in enumerate(self._cards.values()):
            card.grid_forget()
            card.grid(row=i // cols, column=i % cols,
                      padx=(0, CARD_GAP), pady=(0, CARD_GAP))
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_scroll(self, e):
        if e.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif e.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    # ── List management ───────────────────────────────────────────────────────
    def _refresh_list(self):
        prev_sel = self._selected_id
        for w in self._grid_frame.winfo_children():
            w.destroy()
        self._cards = {}

        if not self._machines:
            tk.Label(
                self._grid_frame,
                text="No machines added yet.\nClick  + Add  to get started.",
                bg=BG, fg=TEXT_DIM, font=FONT, justify="center",
            ).pack(pady=60)
        else:
            for m in self._machines:
                card = MachineCard(
                    self._grid_frame, m,
                    on_select=self._select_card,
                    on_double=self._connect_by_id,
                    on_connect=self._connect_by_id,
                    on_edit=self._edit_by_id,
                    on_remove=self._remove_by_id,
                )
                self._cards[m.id] = card

        self._reflow_cards()

        if prev_sel and prev_sel in self._cards:
            self._select_card(prev_sel)
        else:
            self._selected_id = None
        self._update_buttons()

    def _select_card(self, machine_id: str):
        self._selected_id = machine_id
        for mid, card in self._cards.items():
            card.set_selected(mid == machine_id)
        self._update_buttons()

    def _selected_machine(self) -> Machine | None:
        if not self._selected_id:
            return None
        return next((m for m in self._machines if m.id == self._selected_id), None)

    def _update_buttons(self):
        state = "normal" if self._selected_machine() else "disabled"
        self._btn_connect.configure(state=state)
        self._btn_edit.configure(state=state)
        self._btn_delete.configure(state=state)

    def _next_port(self) -> int:
        used = {m.port for m in self._machines}
        port = self._settings.ssh_port_start
        while port in used:
            port += 1
        return port

    # ── Actions ───────────────────────────────────────────────────────────────
    def _add_machine(self):
        dlg = MachineDialog(self, settings=self._settings, next_port=self._next_port())
        self.wait_window(dlg)
        if dlg.result:
            self._machines.append(dlg.result)
            config.save(self._machines, self._settings)
            self._refresh_list()
            self._select_card(dlg.result.id)

    def _edit_machine(self):
        m = self._selected_machine()
        if m:
            self._edit_by_id(m.id)

    def _edit_by_id(self, machine_id: str):
        m = next((x for x in self._machines if x.id == machine_id), None)
        if not m:
            return
        dlg = MachineDialog(self, machine=m, settings=self._settings)
        self.wait_window(dlg)
        if dlg.result:
            idx = next(i for i, x in enumerate(self._machines) if x.id == m.id)
            self._machines[idx] = dlg.result
            config.save(self._machines, self._settings)
            self._refresh_list()

    def _delete_machine(self):
        m = self._selected_machine()
        if m:
            self._remove_by_id(m.id)

    def _remove_by_id(self, machine_id: str):
        m = next((x for x in self._machines if x.id == machine_id), None)
        if not m:
            return
        if messagebox.askyesno("Delete", f"Delete '{m.name}'?", parent=self):
            self._machines = [x for x in self._machines if x.id != m.id]
            config.save(self._machines, self._settings)
            self._refresh_list()

    def _connect(self):
        m = self._selected_machine()
        if m:
            self._connect_by_id(m.id)

    def _connect_by_id(self, machine_id: str):
        m = next((x for x in self._machines if x.id == machine_id), None)
        if not m:
            return
        if connection.is_connected(m.id):
            messagebox.showinfo("Already Connected",
                                f"Already connected to {m.name}.", parent=self)
            return

        self._set_status(f"Connecting to {m.name}…")
        self._btn_connect.configure(state="disabled")

        def on_error(msg):
            self.after(0, lambda: messagebox.showerror("Connection Error", msg, parent=self))
            self.after(0, self._refresh_list)
            self.after(0, lambda: self._set_status(""))

        def on_done():
            self.after(0, self._refresh_list)
            self.after(0, lambda: self._set_status(""))

        def poll_start():
            import time as _t
            _t.sleep(0.5)
            self.after(0, self._refresh_list)

        threading.Thread(target=poll_start, daemon=True).start()
        connection.connect(m, self._settings, on_error=on_error, on_done=on_done)

    def _poll_status(self):
        for card in self._cards.values():
            card.refresh_status()
        self.after(2000, self._poll_status)

    def _open_settings(self):
        old_theme = self._settings.theme
        dlg = SettingsDialog(self, self._settings,
                             on_export=self._export_config,
                             on_import=self._import_config)
        self.wait_window(dlg)
        if dlg.result:
            self._settings = dlg.result
            config.save(self._machines, self._settings)
            if dlg.result.theme != old_theme:
                self.restart_requested = True
                self.destroy()

    def _export_config(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON backup", "*.json"), ("All files", "*.*")],
            initialfile="machineportal_backup.json",
            title="Export Config",
            parent=self,
        )
        if path:
            import shutil
            shutil.copy2(config.CONFIG_FILE, path)
            messagebox.showinfo("Export", f"Config exported to:\n{path}", parent=self)

    def _import_config(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON backup", "*.json"), ("All files", "*.*")],
            title="Import Config",
            parent=self,
        )
        if not path:
            return
        try:
            machines, settings = config.load_from(path)
        except Exception as e:
            messagebox.showerror("Import Failed", str(e), parent=self)
            return
        if not messagebox.askyesno(
            "Import Config",
            f"Replace current config with {len(machines)} machine(s) from backup?",
            parent=self,
        ):
            return
        self._machines  = machines
        self._settings  = settings
        config.save(machines, settings)
        self._refresh_list()
        messagebox.showinfo("Import", "Config imported successfully.", parent=self)

    def _set_status(self, msg: str):
        self._status_lbl.configure(text=msg)

    def _on_close(self):
        self.destroy()
