#!/usr/bin/env python3
"""
Machine Portal — License Generator
Vendor tool for issuing Ed25519-signed license keys.
"""
import base64
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

try:
    from nacl.signing import SigningKey
except ImportError:
    sys.exit("ERROR: Install PyNaCl first:  pip install PyNaCl")

# ── Paths ─────────────────────────────────────────────────────────────────────
_DIR         = os.path.dirname(__file__)
_PRIVATE_KEY = os.path.join(_DIR, "private.key")

# ── Theme ─────────────────────────────────────────────────────────────────────
BG           = "#f5f7f2"
SURFACE      = "#e8eedf"
ACCENT       = "#72b81a"
ACCENT_H     = "#5d9814"
BTN_SEC      = "#c8d4b8"
TEXT         = "#1a1a1a"
TEXT_DIM     = "#555f48"
TEXT_TINY    = "#7a8c6a"
RED          = "#c0392b"
ENTRY_BG     = "#ffffff"
ENTRY_BORDER = "#b0bf9a"

FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_SMALL = ("Segoe UI", 8)


# ── Key generation ────────────────────────────────────────────────────────────

def _load_signing_key() -> SigningKey:
    if not os.path.exists(_PRIVATE_KEY):
        raise FileNotFoundError(
            f"Private key not found:\n{_PRIVATE_KEY}\n\nRun generate_keypair.py first."
        )
    with open(_PRIVATE_KEY) as f:
        return SigningKey(bytes.fromhex(f.read().strip()))


def generate_key(device_id: str, expiry: str) -> str:
    fp8 = device_id.replace("-", "").upper().replace("O", "0")[:8]
    expiry = expiry.upper()
    msg = f"{fp8}|{expiry}".encode()
    sk = _load_signing_key()
    sig = base64.urlsafe_b64encode(sk.sign(msg).signature).rstrip(b"=").decode()
    return f"{fp8}-{expiry}-{sig}"


# ── UI helpers ────────────────────────────────────────────────────────────────

def _btn(parent, text, cmd, bg=None, **kw):
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg or ACCENT, fg="#ffffff" if (bg or ACCENT) == ACCENT else TEXT,
        activebackground=ACCENT_H, activeforeground="#ffffff",
        relief="flat", cursor="hand2", font=FONT_BOLD,
        padx=12, pady=5, **kw,
    )
    b.bind("<Enter>", lambda e: b.configure(bg=ACCENT_H if b["bg"] == ACCENT else b["bg"]))
    b.bind("<Leave>", lambda e: b.configure(bg=bg or ACCENT))
    return b


class LicenseGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Machine Portal — License Generator")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._build()
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build(self):
        tk.Label(self, text="License Generator", bg=BG, fg=ACCENT,
                 font=FONT_TITLE).pack(padx=24, pady=(20, 2))
        tk.Label(self, text="Machine Portal — Vendor Tool", bg=BG, fg=TEXT_TINY,
                 font=FONT_SMALL).pack(padx=24, pady=(0, 12))

        # ── Device ID ────────────────────────────────────────────────────────
        tk.Label(self, text="Device ID", bg=BG, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(padx=24, anchor="w")
        self._id_var = tk.StringVar()
        id_entry = tk.Entry(
            self, textvariable=self._id_var, width=26,
            bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
            relief="flat", highlightthickness=1,
            highlightbackground=ENTRY_BORDER, highlightcolor=ACCENT,
            font=("Courier New", 12),
        )
        id_entry.pack(padx=24, fill="x", pady=(2, 0))
        tk.Label(self, text="Format: XXXX-XXXX-XXXX-XXXX (shown in the activation dialog)",
                 bg=BG, fg=TEXT_TINY, font=FONT_SMALL).pack(padx=24, anchor="w", pady=(3, 10))

        # ── Expiry ───────────────────────────────────────────────────────────
        tk.Label(self, text="Expiry", bg=BG, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(padx=24, anchor="w")

        exp_frame = tk.Frame(self, bg=BG)
        exp_frame.pack(padx=24, fill="x", pady=(2, 0))

        self._expiry_type = tk.StringVar(value="LIFETIME")

        rb_life = tk.Radiobutton(exp_frame, text="Lifetime", variable=self._expiry_type,
                                  value="LIFETIME", bg=BG, fg=TEXT, font=FONT,
                                  activebackground=BG, selectcolor=SURFACE,
                                  command=self._toggle_expiry)
        rb_life.pack(side="left")

        rb_date = tk.Radiobutton(exp_frame, text="Expires on:", variable=self._expiry_type,
                                  value="DATE", bg=BG, fg=TEXT, font=FONT,
                                  activebackground=BG, selectcolor=SURFACE,
                                  command=self._toggle_expiry)
        rb_date.pack(side="left", padx=(12, 6))

        self._date_var = tk.StringVar(value=datetime.today().strftime("%Y%m%d"))
        self._date_entry = tk.Entry(
            exp_frame, textvariable=self._date_var, width=10,
            bg=ENTRY_BG, fg=TEXT_DIM, insertbackground=TEXT,
            relief="flat", highlightthickness=1,
            highlightbackground=ENTRY_BORDER, highlightcolor=ACCENT,
            font=("Courier New", 10), state="disabled",
        )
        self._date_entry.pack(side="left")
        tk.Label(exp_frame, text="YYYYMMDD", bg=BG, fg=TEXT_TINY,
                 font=FONT_SMALL).pack(side="left", padx=(6, 0))

        # ── Generate button ───────────────────────────────────────────────────
        _btn(self, "Generate License Key", self._generate).pack(
            padx=24, pady=(16, 8), fill="x")

        # ── Result box ───────────────────────────────────────────────────────
        result_frame = tk.Frame(self, bg=SURFACE, padx=14, pady=12)
        result_frame.pack(padx=24, pady=(0, 6), fill="x")

        tk.Label(result_frame, text="License Key", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w")

        key_row = tk.Frame(result_frame, bg=SURFACE)
        key_row.pack(fill="x", pady=(4, 0))

        self._key_var = tk.StringVar()
        key_display = tk.Entry(
            key_row, textvariable=self._key_var, state="readonly",
            bg=SURFACE, fg=TEXT, relief="flat",
            font=("Courier New", 8),
            readonlybackground=SURFACE,
        )
        key_display.pack(side="left", fill="x", expand=True)

        self._copy_btn = _btn(key_row, "Copy", self._copy, bg=BTN_SEC, width=6)
        self._copy_btn.pack(side="left", padx=(8, 0))

        self._status = tk.Label(self, text="", bg=BG, fg=TEXT_TINY, font=FONT_SMALL)
        self._status.pack(padx=24, anchor="w", pady=(0, 20))

    def _toggle_expiry(self):
        if self._expiry_type.get() == "DATE":
            self._date_entry.configure(state="normal", fg=TEXT)
        else:
            self._date_entry.configure(state="disabled", fg=TEXT_DIM)

    def _generate(self):
        device_id = self._id_var.get().strip()
        if not device_id:
            self._set_status("Enter a Device ID.", error=True)
            return

        clean = device_id.replace("-", "").upper().replace("O", "0")
        if len(clean) < 8:
            self._set_status("Device ID is too short (need at least 8 characters).", error=True)
            return

        if self._expiry_type.get() == "DATE":
            expiry = self._date_var.get().strip()
            try:
                datetime.strptime(expiry, "%Y%m%d")
            except ValueError:
                self._set_status("Invalid date — use YYYYMMDD format.", error=True)
                return
        else:
            expiry = "LIFETIME"

        try:
            key = generate_key(device_id, expiry)
        except FileNotFoundError as e:
            messagebox.showerror("Private Key Missing", str(e))
            return
        except Exception as e:
            self._set_status(f"Error: {e}", error=True)
            return

        self._key_var.set(key)
        exp_label = "never expires" if expiry == "LIFETIME" else \
                    f"expires {expiry[:4]}-{expiry[4:6]}-{expiry[6:]}"
        self._set_status(f"Key generated — {exp_label}.")

    def _copy(self):
        key = self._key_var.get()
        if not key:
            return
        self.clipboard_clear()
        self.clipboard_append(key)
        self._copy_btn.configure(text="Copied!")
        self.after(1500, lambda: self._copy_btn.configure(text="Copy"))

    def _set_status(self, msg, error=False):
        self._status.configure(text=msg, fg=RED if error else TEXT_TINY)


if __name__ == "__main__":
    LicenseGeneratorApp().mainloop()
