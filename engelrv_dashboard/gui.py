import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading

import config
import connection
from config import Machine, Settings


# ── Colours & fonts ──────────────────────────────────────────────────────────
BG = "#1e1e2e"
SURFACE = "#2a2a3e"
ACCENT = "#7c6af7"
ACCENT_HOVER = "#9d8fff"
TEXT = "#e0e0f0"
TEXT_DIM = "#888aaa"
GREEN = "#4caf83"
RED = "#e05c5c"
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")


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
        bg=bg, fg=fg, activebackground=ACCENT_HOVER, activeforeground="white",
        relief="flat", font=FONT_BOLD, padx=8, pady=4, width=width, cursor="hand2",
    )
    b.bind("<Enter>", lambda e: b.configure(bg=ACCENT_HOVER))
    b.bind("<Leave>", lambda e: b.configure(bg=bg))
    return b


# ── Add / Edit dialog ─────────────────────────────────────────────────────────
class MachineDialog(tk.Toplevel):
    def __init__(self, parent, machine: Machine | None = None):
        super().__init__(parent)
        self.result: Machine | None = None
        self._machine = machine

        self.title("Edit Machine" if machine else "Add Machine")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        pad = {"padx": 12, "pady": 5}

        def lbl(text):
            return tk.Label(self, text=text, bg=BG, fg=TEXT_DIM, font=FONT, anchor="w")

        # Name
        lbl("Machine Name").grid(row=0, column=0, sticky="w", **pad)
        self._name = tk.Entry(self, width=30)
        _style_entry(self._name)
        self._name.grid(row=0, column=1, **pad)

        # IP
        lbl("IP Address").grid(row=1, column=0, sticky="w", **pad)
        self._ip = tk.Entry(self, width=30)
        _style_entry(self._ip)
        self._ip.grid(row=1, column=1, **pad)

        # SSH toggle
        self._ssh_var = tk.BooleanVar(value=machine.ssh if machine else False)
        ssh_chk = tk.Checkbutton(
            self, text="Requires SSH tunnel", variable=self._ssh_var,
            command=self._toggle_ssh,
            bg=BG, fg=TEXT, selectcolor=SURFACE, activebackground=BG,
            activeforeground=TEXT, font=FONT,
        )
        ssh_chk.grid(row=2, column=0, columnspan=2, sticky="w", padx=12, pady=6)

        # SSH user
        self._user_lbl = lbl("SSH Username")
        self._user_lbl.grid(row=3, column=0, sticky="w", **pad)
        self._user = tk.Entry(self, width=30)
        _style_entry(self._user)
        self._user.grid(row=3, column=1, **pad)

        # SSH password
        self._pass_lbl = lbl("SSH Password")
        self._pass_lbl.grid(row=4, column=0, sticky="w", **pad)
        self._password = tk.Entry(self, width=30, show="•")
        _style_entry(self._password)
        self._password.grid(row=4, column=1, **pad)

        # Buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=12)
        _btn(btn_frame, "Save", self._save, width=10).pack(side="left", padx=6)
        _btn(btn_frame, "Cancel", self.destroy, bg="#44446a", width=10).pack(side="left", padx=6)

        # Pre-fill
        if machine:
            self._name.insert(0, machine.name)
            self._ip.insert(0, machine.ip)
            self._user.insert(0, machine.ssh_user)
            self._password.insert(0, machine.ssh_password)

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
        state = "normal" if self._ssh_var.get() else "disabled"
        self._user.configure(state=state)
        self._password.configure(state=state)
        dim = TEXT if self._ssh_var.get() else "#555577"
        self._user_lbl.configure(fg=dim)
        self._pass_lbl.configure(fg=dim)

    def _save(self):
        name = self._name.get().strip()
        ip = self._ip.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Machine name is required.", parent=self)
            return
        if not ip:
            messagebox.showwarning("Validation", "IP address is required.", parent=self)
            return

        self.result = Machine(
            name=name,
            ip=ip,
            ssh=self._ssh_var.get(),
            ssh_user=self._user.get().strip() or "user",
            ssh_password=self._password.get(),
            id=self._machine.id if self._machine else __import__("uuid").uuid4().__str__(),
        )
        self.destroy()


# ── Main window ───────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EngelRV — Remote View Dashboard")
        self.geometry("560x400")
        self.minsize(480, 320)
        self.configure(bg=BG)

        self._machines, self._settings = config.load()
        self._build_ui()
        self._refresh_list()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self, bg=BG)
        title_frame.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(title_frame, text="EngelRV", bg=BG, fg=ACCENT, font=FONT_TITLE).pack(side="left")
        tk.Label(title_frame, text="Remote View Dashboard", bg=BG, fg=TEXT_DIM, font=FONT).pack(
            side="left", padx=(8, 0), pady=2
        )
        _btn(title_frame, "+ Add", self._add_machine, width=8).pack(side="right")

        # Machine list
        list_frame = tk.Frame(self, bg=SURFACE, bd=0, relief="flat")
        list_frame.pack(fill="both", expand=True, padx=16, pady=4)

        cols = ("status", "name", "ip", "type")
        self._tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=SURFACE, foreground=TEXT, fieldbackground=SURFACE,
            font=FONT, rowheight=28, borderwidth=0,
        )
        style.configure("Treeview.Heading", background=BG, foreground=TEXT_DIM, font=FONT_BOLD)
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])

        self._tree.heading("status", text="")
        self._tree.heading("name", text="Machine")
        self._tree.heading("ip", text="IP Address")
        self._tree.heading("type", text="Connection")
        self._tree.column("status", width=24, stretch=False, anchor="center")
        self._tree.column("name", width=180, anchor="w")
        self._tree.column("ip", width=140, anchor="w")
        self._tree.column("type", width=100, anchor="center")

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._tree.bind("<Double-1>", lambda e: self._connect())
        self._tree.bind("<<TreeviewSelect>>", lambda e: self._update_buttons())

        # Bottom toolbar
        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", padx=16, pady=(6, 14))

        self._btn_connect = _btn(toolbar, "Connect", self._connect, width=10)
        self._btn_connect.pack(side="left", padx=(0, 6))
        self._btn_edit = _btn(toolbar, "Edit", self._edit_machine, bg="#44446a", width=8)
        self._btn_edit.pack(side="left", padx=(0, 6))
        self._btn_delete = _btn(toolbar, "Delete", self._delete_machine, bg=RED, width=8)
        self._btn_delete.pack(side="left")

        self._status_lbl = tk.Label(toolbar, text="", bg=BG, fg=TEXT_DIM, font=FONT)
        self._status_lbl.pack(side="right")

        self._update_buttons()

    # ── List management ───────────────────────────────────────────────────────
    def _refresh_list(self):
        selected_id = self._selected_id()
        for row in self._tree.get_children():
            self._tree.delete(row)

        for m in self._machines:
            active = connection.is_connected(m.id)
            dot = "●" if active else "○"
            conn_type = "SSH + VNC" if m.ssh else "Direct VNC"
            iid = self._tree.insert(
                "", "end", iid=m.id,
                values=(dot, m.name, m.ip, conn_type),
                tags=("active",) if active else (),
            )

        self._tree.tag_configure("active", foreground=GREEN)

        if selected_id and self._tree.exists(selected_id):
            self._tree.selection_set(selected_id)

        self._update_buttons()

    def _selected_id(self) -> str | None:
        sel = self._tree.selection()
        return sel[0] if sel else None

    def _selected_machine(self) -> Machine | None:
        mid = self._selected_id()
        if not mid:
            return None
        return next((m for m in self._machines if m.id == mid), None)

    def _update_buttons(self):
        m = self._selected_machine()
        state = "normal" if m else "disabled"
        self._btn_connect.configure(state=state)
        self._btn_edit.configure(state=state)
        self._btn_delete.configure(state=state)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _add_machine(self):
        dlg = MachineDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self._machines.append(dlg.result)
            config.save(self._machines, self._settings)
            self._refresh_list()
            self._tree.selection_set(dlg.result.id)

    def _edit_machine(self):
        m = self._selected_machine()
        if not m:
            return
        dlg = MachineDialog(self, machine=m)
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
        if not m:
            return

        if connection.is_connected(m.id):
            messagebox.showinfo("Already Connected", f"Already connected to {m.name}.", parent=self)
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
            # Give the thread a moment to register the connection, then refresh
            import time as _t
            _t.sleep(0.5)
            self.after(0, self._refresh_list)

        threading.Thread(target=poll_start, daemon=True).start()
        connection.connect(m, self._settings, on_error=on_error, on_done=on_done)

    def _set_status(self, msg: str):
        self._status_lbl.configure(text=msg)

    def _on_close(self):
        self.destroy()
