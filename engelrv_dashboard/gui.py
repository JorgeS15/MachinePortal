import tkinter as tk
from tkinter import ttk, messagebox
import threading

import config
import connection
from config import Machine, Settings

# ── Colours & fonts ───────────────────────────────────────────────────────────
BG        = "#1e1e2e"
SURFACE   = "#2a2a3e"
CARD_BG   = "#252538"
ACCENT    = "#7c6af7"
ACCENT_H  = "#9d8fff"
TEXT      = "#e0e0f0"
TEXT_DIM  = "#888aaa"
GREEN     = "#4caf83"
RED       = "#e05c5c"
FONT      = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE= ("Segoe UI", 13, "bold")
FONT_SMALL= ("Segoe UI", 8)
FONT_CARD = ("Segoe UI", 9)

CARD_W  = 172
CARD_H  = 150
THUMB_H = 108
CARD_GAP = 14


def _style_entry(w):
    w.configure(
        bg=SURFACE, fg=TEXT, insertbackground=TEXT,
        relief="flat", highlightthickness=1,
        highlightbackground="#44446a", highlightcolor=ACCENT,
        font=FONT,
    )


def _btn(parent, text, cmd, bg=ACCENT, fg="white", width=12):
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, activebackground=ACCENT_H, activeforeground="white",
        relief="flat", font=FONT_BOLD, padx=8, pady=4, width=width, cursor="hand2",
    )
    b.bind("<Enter>", lambda e: b.configure(bg=ACCENT_H))
    b.bind("<Leave>", lambda e: b.configure(bg=bg))
    return b


# ── Machine card widget ───────────────────────────────────────────────────────
class MachineCard(tk.Frame):

    def __init__(self, parent, machine: Machine, on_select, on_double):
        super().__init__(
            parent,
            width=CARD_W, height=CARD_H,
            bg=CARD_BG,
            cursor="hand2",
            highlightthickness=2,
            highlightbackground=CARD_BG,
        )
        self.pack_propagate(False)
        self.machine = machine
        self._on_select = on_select
        self._on_double = on_double

        # Thumbnail canvas
        self._thumb = tk.Canvas(
            self, width=CARD_W - 4, height=THUMB_H,
            bg="#1a1a2c", highlightthickness=0,
        )
        self._thumb.pack(fill="x")
        self._draw_thumb()

        # Info strip
        info = tk.Frame(self, bg=CARD_BG)
        info.pack(fill="x", padx=7, pady=(5, 4))

        connected = connection.is_connected(machine.id)
        self._dot = tk.Label(
            info, text="●", bg=CARD_BG,
            fg=GREEN if connected else TEXT_DIM,
            font=FONT_SMALL,
        )
        self._dot.pack(side="left")
        tk.Label(
            info, text=machine.name, bg=CARD_BG, fg=TEXT,
            font=FONT_CARD, anchor="w",
        ).pack(side="left", padx=(3, 0))

        self._bind_tree(self)

    def _draw_thumb(self):
        c = self._thumb
        w, h = CARD_W - 4, THUMB_H
        # Monitor screen
        sx, sy = w * 0.13, h * 0.08
        sw, sh = w * 0.74, h * 0.66
        c.create_rectangle(sx, sy, sx + sw, sy + sh,
                           outline="#44446a", fill="#2a2a3e", width=2)
        # Stand stem
        mx = w / 2
        c.create_line(mx, sy + sh, mx, sy + sh + h * 0.14,
                      fill="#44446a", width=3)
        # Stand base
        bw = sw * 0.38
        by = sy + sh + h * 0.14
        c.create_rectangle(mx - bw, by, mx + bw, by + h * 0.1,
                           fill="#44446a", outline="")
        # Initials
        parts = self.machine.name.split()
        initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()
        c.create_text(w / 2, sy + sh / 2,
                      text=initials, fill="#5a5a90",
                      font=("Segoe UI", 18, "bold"))

    def _bind_tree(self, widget):
        widget.bind("<Button-1>", lambda e: self._on_select(self.machine.id))
        widget.bind("<Double-Button-1>", lambda e: self._on_double(self.machine.id))
        for child in widget.winfo_children():
            self._bind_tree(child)

    def refresh_status(self):
        connected = connection.is_connected(self.machine.id)
        self._dot.configure(fg=GREEN if connected else TEXT_DIM)

    def set_selected(self, selected: bool):
        connected = connection.is_connected(self.machine.id)
        if selected:
            self.configure(highlightbackground=ACCENT)
        elif connected:
            self.configure(highlightbackground=GREEN)
        else:
            self.configure(highlightbackground=CARD_BG)


# ── Add / Edit machine dialog ─────────────────────────────────────────────────
class MachineDialog(tk.Toplevel):

    def __init__(self, parent, machine: Machine | None = None,
                 settings: Settings | None = None, next_port: int = 10062):
        super().__init__(parent)
        self.result: Machine | None = None
        self._machine = machine
        self._settings = settings or Settings()

        self.title("Edit Machine" if machine else "Add Machine")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        pad = {"padx": 12, "pady": 5}

        def lbl(text):
            return tk.Label(self, text=text, bg=BG, fg=TEXT_DIM, font=FONT, anchor="w")

        lbl("Machine Name").grid(row=0, column=0, sticky="w", **pad)
        self._name = tk.Entry(self, width=30)
        _style_entry(self._name)
        self._name.grid(row=0, column=1, **pad)

        lbl("IP Address").grid(row=1, column=0, sticky="w", **pad)
        self._ip = tk.Entry(self, width=30)
        _style_entry(self._ip)
        self._ip.grid(row=1, column=1, **pad)

        self._ssh_var = tk.BooleanVar(value=machine.ssh if machine else False)
        tk.Checkbutton(
            self, text="Requires SSH tunnel", variable=self._ssh_var,
            command=self._toggle_ssh,
            bg=BG, fg=TEXT, selectcolor=SURFACE,
            activebackground=BG, activeforeground=TEXT, font=FONT,
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=12, pady=6)

        self._user_lbl = lbl("SSH Username")
        self._user_lbl.grid(row=3, column=0, sticky="w", **pad)
        self._user = tk.Entry(self, width=30)
        _style_entry(self._user)
        self._user.grid(row=3, column=1, **pad)

        self._pass_lbl = lbl("SSH Password")
        self._pass_lbl.grid(row=4, column=0, sticky="w", **pad)
        self._password = tk.Entry(self, width=30, show="•")
        _style_entry(self._password)
        self._password.grid(row=4, column=1, **pad)

        self._port_lbl = lbl("SSH local port")
        self._port_lbl.grid(row=5, column=0, sticky="w", **pad)
        self._port = tk.Entry(self, width=30)
        _style_entry(self._port)
        self._port.grid(row=5, column=1, **pad)

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=12)
        _btn(btn_frame, "Save", self._save, width=10).pack(side="left", padx=6)
        _btn(btn_frame, "Cancel", self.destroy, bg="#44446a", width=10).pack(side="left", padx=6)

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
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _toggle_ssh(self):
        ssh = self._ssh_var.get()
        state = "normal" if ssh else "disabled"
        dim = TEXT if ssh else "#555577"
        for w in (self._user, self._password, self._port):
            w.configure(state=state)
        for lbl in (self._user_lbl, self._pass_lbl, self._port_lbl):
            lbl.configure(fg=dim)

    def _save(self):
        name = self._name.get().strip()
        ip = self._ip.get().strip()
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
            name=name,
            ip=ip,
            ssh=self._ssh_var.get(),
            ssh_user=self._user.get().strip() or "user",
            ssh_password=self._password.get(),
            port=port,
            id=self._machine.id if self._machine else __import__("uuid").uuid4().__str__(),
        )
        self.destroy()


# ── Settings dialog ───────────────────────────────────────────────────────────
class SettingsDialog(tk.Toplevel):

    def __init__(self, parent, settings: Settings):
        super().__init__(parent)
        self.result: Settings | None = None

        self.title("Settings")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        pad = {"padx": 14, "pady": 5}
        row = [0]

        def section(title):
            tk.Label(
                self, text=title, bg=BG, fg=ACCENT, font=FONT_BOLD,
            ).grid(row=row[0], column=0, columnspan=2, sticky="w",
                   padx=14, pady=(14 if row[0] == 0 else 10, 2))
            row[0] += 1

        def field(label, default, show=None):
            tk.Label(self, text=label, bg=BG, fg=TEXT_DIM, font=FONT, anchor="w").grid(
                row=row[0], column=0, sticky="w", **pad)
            e = tk.Entry(self, width=22, show=show)
            _style_entry(e)
            e.insert(0, str(default))
            e.grid(row=row[0], column=1, **pad)
            row[0] += 1
            return e

        section("SSH / Tunnel")
        self._port_start  = field("Starting SSH port",  settings.ssh_port_start)
        self._remote_port = field("Remote VNC port",    settings.ssh_remote_port)
        self._wait        = field("Tunnel wait (sec)",   settings.tunnel_wait_seconds)

        section("Direct VNC")
        self._vnc_port = field("VNC port", settings.vnc_port)

        section("Default Credentials")
        self._def_user = field("Default SSH user",     settings.default_ssh_user)
        self._def_pass = field("Default SSH password", settings.default_ssh_password, show="•")

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.grid(row=row[0], column=0, columnspan=2, pady=14)
        _btn(btn_frame, "Save", self._save, width=10).pack(side="left", padx=6)
        _btn(btn_frame, "Cancel", self.destroy, bg="#44446a", width=10).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())
        self._center(parent)

    def _center(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
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
            )
            self.destroy()
        except ValueError:
            messagebox.showwarning(
                "Validation", "Port and wait values must be integers.", parent=self)


# ── Main window ───────────────────────────────────────────────────────────────
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("EngelRV — Remote View Dashboard")
        self.geometry("720x520")
        self.minsize(560, 380)
        self.configure(bg=BG)

        self._machines, self._settings = config.load()
        self._cards: dict[str, MachineCard] = {}
        self._selected_id: str | None = None

        self._build_ui()
        self._refresh_list()
        self.after(120, self._reflow_cards)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self, bg=BG)
        title_frame.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(title_frame, text="EngelRV", bg=BG, fg=ACCENT,
                 font=FONT_TITLE).pack(side="left")
        tk.Label(title_frame, text="Remote View Dashboard", bg=BG, fg=TEXT_DIM,
                 font=FONT).pack(side="left", padx=(8, 0), pady=2)
        _btn(title_frame, "+ Add", self._add_machine, width=8).pack(side="right")

        # Scrollable card grid
        grid_container = tk.Frame(self, bg=BG)
        grid_container.pack(fill="both", expand=True, padx=16, pady=4)

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

        # Bottom toolbar
        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", padx=16, pady=(6, 14))

        self._btn_connect = _btn(toolbar, "Connect", self._connect, width=10)
        self._btn_connect.pack(side="left", padx=(0, 6))
        self._btn_edit = _btn(toolbar, "Edit", self._edit_machine, bg="#44446a", width=8)
        self._btn_edit.pack(side="left", padx=(0, 6))
        self._btn_delete = _btn(toolbar, "Delete", self._delete_machine, bg=RED, width=8)
        self._btn_delete.pack(side="left")

        _btn(toolbar, "⚙ Settings", self._open_settings,
             bg=SURFACE, width=10).pack(side="right")

        self._status_lbl = tk.Label(toolbar, text="", bg=BG, fg=TEXT_DIM, font=FONT)
        self._status_lbl.pack(side="right", padx=(0, 10))

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
            card.grid(
                row=i // cols, column=i % cols,
                padx=(0, CARD_GAP), pady=(0, CARD_GAP),
            )
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

        for m in self._machines:
            card = MachineCard(
                self._grid_frame, m,
                on_select=self._select_card,
                on_double=self._connect_by_id,
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
            messagebox.showinfo(
                "Already Connected", f"Already connected to {m.name}.", parent=self)
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

    def _open_settings(self):
        dlg = SettingsDialog(self, self._settings)
        self.wait_window(dlg)
        if dlg.result:
            self._settings = dlg.result
            config.save(self._machines, self._settings)

    def _set_status(self, msg: str):
        self._status_lbl.configure(text=msg)

    def _on_close(self):
        self.destroy()
