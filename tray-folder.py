import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow
from PyQt5.QtGui import QIcon
import os

class SystemTrayApp(QMainWindow):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.icon_state = 0
        self.icons = ["assets/up.png", "assets/down.png"]

        # Hide main window
        self.hide()
        

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.icons[self.icon_state]))  # Set initial icon
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.build_tray_menu()
        self.tray_icon.show()

    def build_tray_menu(self):
        menu = QMenu()

        for item in os.listdir(self.folder_path):
            item_action = QAction(item, self)
            item_action.triggered.connect(lambda checked, item=item: self.open_item(item))
            menu.addAction(item_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(app.quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            # Toggle icon
            self.icon_state = 1 - self.icon_state
            self.tray_icon.setIcon(QIcon(self.icons[self.icon_state]))

            # Show context menu
            self.tray_icon.contextMenu().popup(self.tray_icon.geometry().bottomLeft())

            self.build_tray_menu()

    def open_item(self, item):
        os.startfile(os.path.join(self.folder_path, item))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemTrayApp("D:\@Portable\[EXTRAFILES]\[shortcuts]")  # Set the folder path
    sys.exit(app.exec_())
