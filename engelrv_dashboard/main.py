import sys
import os

# When running from PyInstaller bundle, add the _MEIPASS dir to the path
# so that config/connection/gui can be imported.
if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)  # type: ignore[attr-defined]
else:
    sys.path.insert(0, os.path.dirname(__file__))

from gui import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
