import sys
import os

if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)  # type: ignore[attr-defined]
else:
    sys.path.insert(0, os.path.dirname(__file__))

from gui import App

if __name__ == "__main__":
    while True:
        app = App()
        app.mainloop()
        if not getattr(app, "restart_requested", False):
            break
