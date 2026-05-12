import sys
import os

if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)  # type: ignore[attr-defined]
else:
    sys.path.insert(0, os.path.dirname(__file__))

import tkinter as tk

import licensing
from gui import App, ActivationDialog


def _is_licensed() -> bool:
    valid, _ = licensing.check_license()
    if valid:
        return True
    root = tk.Tk()
    root.withdraw()
    dlg = ActivationDialog(root)
    root.wait_window(dlg)
    root.destroy()
    return dlg.activated


if __name__ == "__main__":
    if not _is_licensed():
        sys.exit(0)

    while True:
        app = App()
        app.mainloop()
        if not getattr(app, "restart_requested", False):
            break
