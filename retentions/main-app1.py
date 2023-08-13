import sys
import os

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication([])

    # Ensure app doesn't prematurely exit
    app.setQuitOnLastWindowClosed(False)

    # Create a system tray icon
    tray = QSystemTrayIcon(QIcon(resource_path("assets/up.png")))
    tray.setToolTip("Tray Example")

    # Create a menu
    menu = QMenu()
    exit_action = menu.addAction("Exit")
    exit_action.triggered.connect(app.quit)
    tray.setContextMenu(menu)

    # Show the system tray icon
    tray.show()
    
    sys.exit(app.exec())
