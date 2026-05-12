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

# ── Colours & fonts ───────────────────────────────────────────────────────────
BG        = "#1e1e2e"
SURFACE   = "#2a2a3e"
CARD_BG   = "#252538"
CARD_HOV  = "#2d2d48"
ACCENT    = "#7c6af7"
ACCENT_H  = "#9d8fff"
TEAL      = "#2a8a7f"
TEXT      = "#e0e0f0"
TEXT_DIM  = "#888aaa"
TEXT_TINY = "#555575"
GREEN     = "#4caf83"
RED       = "#e05c5c"
FONT      = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE= ("Segoe UI", 13, "bold")
FONT_SMALL= ("Segoe UI", 8)
FONT_CARD = ("Segoe UI", 9)
FONT_TINY = ("Segoe UI", 7)

CARD_W   = 172
CARD_H   = 164
THUMB_H  = 106
CARD_GAP = 14

# App icon – 64×64 RGBA PNG, embedded as base64 so no external file needed.
_ICON_B64 = (
    "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"
    "/DFKvgAAAABJRU5ErkJggg=="
)


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


def _separator(parent, color="#2e2e48"):
    tk.Frame(parent, bg=color, height=1).pack(fill="x")


# ── Machine card widget ───────────────────────────────────────────────────────
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
        self.machine = machine
        self._on_select  = on_select
        self._on_double  = on_double
        self._on_connect = on_connect
        self._on_edit    = on_edit
        self._on_remove  = on_remove
        self._selected = False

        # ── Thumbnail ──────────────────────────────────────────────────────
        self._thumb = tk.Canvas(
            self, width=CARD_W - 4, height=THUMB_H,
            bg="#191928", highlightthickness=0,
        )
        self._thumb.pack(fill="x")
        self._draw_thumb()

        # ── Info strip ─────────────────────────────────────────────────────
        info = tk.Frame(self, bg=CARD_BG)
        info.pack(fill="x", padx=8, pady=(6, 4))

        ping = connection.get_ping_state(machine.id)
        dot_color = GREEN if ping is True else (RED if ping is False else TEXT_DIM)
        self._dot = tk.Label(
            info, text="●", bg=CARD_BG,
            fg=dot_color,
            font=FONT_SMALL,
        )
        self._dot.pack(side="left")
        tk.Label(
            info, text=machine.name, bg=CARD_BG, fg=TEXT,
            font=FONT_CARD, anchor="w",
        ).pack(side="left", padx=(3, 0))

        # ── Second row: IP + badge ─────────────────────────────────────────
        meta = tk.Frame(self, bg=CARD_BG)
        meta.pack(fill="x", padx=8, pady=(0, 6))

        tk.Label(
            meta, text=machine.ip, bg=CARD_BG, fg=TEXT_DIM,
            font=FONT_TINY, anchor="w",
        ).pack(side="left")

        badge_bg  = ACCENT if machine.ssh else TEAL
        badge_txt = "SSH+VNC" if machine.ssh else "Direct VNC"
        badge = tk.Label(
            meta, text=badge_txt, bg=badge_bg, fg="white",
            font=FONT_TINY, padx=4, pady=1,
        )
        badge.pack(side="right")

        self._bind_tree(self)

    def _draw_thumb(self):
        c = self._thumb
        w, h = CARD_W - 4, THUMB_H
        # Monitor screen
        sx, sy = int(w*.13), int(h*.10)
        sw, sh = int(w*.74), int(h*.64)
        # Subtle inner glow: slightly lighter fill at top
        c.create_rectangle(sx+2, sy+2, sx+sw-2, sy+sh-2, fill="#23233a", outline="")
        c.create_rectangle(sx, sy, sx+sw, sy+sh,
                           outline="#4a4875", fill="", width=2)
        # Stand stem
        mx = w // 2
        c.create_line(mx, sy+sh, mx, sy+sh+int(h*.14), fill="#4a4875", width=3)
        # Stand base
        bw = int(sw * .36)
        by = sy + sh + int(h*.14)
        c.create_rectangle(mx-bw, by, mx+bw, by+int(h*.10),
                           fill="#4a4875", outline="")
        # Initials inside screen
        parts = self.machine.name.split()
        initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()
        c.create_text(w/2, sy + sh/2,
                      text=initials, fill="#5a5a98",
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
                       activeforeground="white", relief="flat",
                       font=FONT, bd=0)
        menu.add_command(label="Connect",
                         command=lambda: self._on_connect(self.machine.id))
        menu.add_separator()
        menu.add_command(label="Edit",
                         command=lambda: self._on_edit(self.machine.id))
        menu.add_command(label="Remove",
                         foreground=RED, activeforeground=RED,
                         command=lambda: self._on_remove(self.machine.id))
        menu.tk_popup(event.x_root, event.y_root)

    def _on_hover_in(self, _e):
        if not self._selected and not connection.is_connected(self.machine.id):
            self.configure(highlightbackground="#44446a")

    def _on_hover_out(self, _e):
        if not self._selected and not connection.is_connected(self.machine.id):
            self.configure(highlightbackground=CARD_BG)

    def refresh_status(self):
        state = connection.get_ping_state(self.machine.id)
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
        dim   = TEXT if ssh else "#555577"
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

        section("Backup & Restore")
        br = tk.Frame(self, bg=BG)
        br.grid(row=row[0], column=0, columnspan=2, padx=14, pady=5, sticky="w")
        _btn(br, "Export…", on_export or (lambda: None), bg="#44446a", width=10).pack(side="left", padx=(0, 8))
        _btn(br, "Import…", on_import or (lambda: None), bg="#44446a", width=10).pack(side="left")
        row[0] += 1

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
        self.geometry("760x540")
        self.minsize(580, 400)
        self.configure(bg=BG)

        # Window icon — prefer .ico (correct Windows taskbar support)
        try:
            ico = _asset_path("engelrv.ico")
            if os.path.exists(ico):
                self.wm_iconbitmap(ico)
            else:
                raise FileNotFoundError
        except Exception:
            try:
                self.iconphoto(True, tk.PhotoImage(data=_ICON_B64))
            except Exception:
                pass

        self._machines, self._settings = config.load()
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
        # ── Title bar ─────────────────────────────────────────────────────
        title_frame = tk.Frame(self, bg=BG)
        title_frame.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(title_frame, text="EngelRV", bg=BG, fg=ACCENT,
                 font=FONT_TITLE).pack(side="left")
        tk.Label(title_frame, text="Remote View Dashboard", bg=BG, fg=TEXT_DIM,
                 font=FONT).pack(side="left", padx=(8, 0), pady=2)
        _btn(title_frame, "+ Add", self._add_machine, width=8).pack(side="right")

        _separator(self)

        # ── Scrollable card grid ───────────────────────────────────────────
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

        # ── Bottom toolbar ─────────────────────────────────────────────────
        _separator(self)

        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", padx=16, pady=(8, 6))

        self._btn_connect = _btn(toolbar, "Connect", self._connect, width=10)
        self._btn_connect.pack(side="left", padx=(0, 6))
        self._btn_edit = _btn(toolbar, "Edit", self._edit_machine, bg="#44446a", width=8)
        self._btn_edit.pack(side="left", padx=(0, 6))
        self._btn_delete = _btn(toolbar, "Delete", self._delete_machine, bg=RED, width=8)
        self._btn_delete.pack(side="left")

        _btn(toolbar, "⚙  Settings", self._open_settings,
             bg=SURFACE, width=11).pack(side="right")

        self._status_lbl = tk.Label(toolbar, text="", bg=BG, fg=TEXT_DIM, font=FONT)
        self._status_lbl.pack(side="right", padx=(0, 10))

        # ── Version footer ─────────────────────────────────────────────────
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

    def _poll_status(self):
        for card in self._cards.values():
            card.refresh_status()
        self.after(2000, self._poll_status)

    def _open_settings(self):
        dlg = SettingsDialog(self, self._settings,
                             on_export=self._export_config,
                             on_import=self._import_config)
        self.wait_window(dlg)
        if dlg.result:
            self._settings = dlg.result
            config.save(self._machines, self._settings)

    def _export_config(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON backup", "*.json"), ("All files", "*.*")],
            initialfile="engelrv_backup.json",
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
        self._machines = machines
        self._settings = settings
        config.save(machines, settings)
        self._refresh_list()
        messagebox.showinfo("Import", "Config imported successfully.", parent=self)

    def _set_status(self, msg: str):
        self._status_lbl.configure(text=msg)

    def _on_close(self):
        self.destroy()
