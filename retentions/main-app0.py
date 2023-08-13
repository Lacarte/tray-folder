import os
import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ExtendedSystemTray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        
        # Setting default icon
        self.setIcon(QIcon(resource_path("assets/up.png")))
        self.setToolTip("Extended Tray Example")
        
        # Setting up context menu
        self.menu = QMenu()
        
        show_notification_action = self.menu.addAction("Show Notification")
        show_notification_action.triggered.connect(self.show_notification)
        
        toggle_icon_action = self.menu.addAction("Toggle Icon")
        toggle_icon_action.triggered.connect(self.toggle_icon)
        
        exit_action = self.menu.addAction("Exit")
        exit_action.triggered.connect(app.quit)
        
        self.setContextMenu(self.menu)
        
        # Show the system tray icon
        self.show()
        
    def show_notification(self):
        """ Show a notification from the system tray """
        self.showMessage("Notification", "This is a notification from Extended Tray!", QIcon(resource_path("assets/up.png")), 3000)
        
    def toggle_icon(self):
        """ Toggle between two icons """
        if self.icon().name() == QIcon(resource_path("assets/up.png")).name():
            self.setIcon(QIcon(resource_path("assets/up-open.png")))
        else:
            self.setIcon(QIcon(resource_path("assets/up.png")))

if __name__ == "__main__":
    app = QApplication([])
    
    # Ensure app doesn't prematurely exit
    app.setQuitOnLastWindowClosed(False)

    tray = ExtendedSystemTray()
    
    sys.exit(app.exec())
