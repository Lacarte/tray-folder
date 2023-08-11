import sys
import os
from datetime import datetime
import logging
from link_checker import is_link_to_directory

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow
from PyQt6.QtWidgets import QLabel, QWidgetAction, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt, QEvent

# Create the "logs" directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"logs/log-{datetime.now().strftime('%Y-%m-%d')}.log",
            mode="w",
        ),
        logging.StreamHandler(),
    ],
)


class SystemTrayApp(QMainWindow):

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.icon_state = 0
        self.icons = ["assets/up.png", "assets/up-open.png"]
        self.menu_visible = False

        # Hide main window
        self.hide()

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.icons[self.icon_state]))
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.build_tray_menu()
        self.tray_icon.show()

    def build_tray_menu(self):
        menu = QMenu()
        menu.installEventFilter(self)

        # Apply CSS Styling to Menu
        menu.setStyleSheet("""
            QMenu {
                background-color: #333;
                color: #EEE;
                padding: 10px;
                border: 1px solid #555;
            }

            QMenu::item {
                padding: 5px 50x 5px 5px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: #555;
            }
                                       
        """)

        # Add title to the menu using QWidgetAction with a QLabel
        title_widget = QWidgetAction(self)
        # Disabling the action to make it unclickable
        title_widget.setDisabled(True)

        # Creating a custom widget for the title
        title_container = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Tray-Folder")

        # Adjusting font size and centering text
        label.setStyleSheet("background-color: transparent; color: #EEE; padding: 1px; font-size: 12px;")
        # This ensures the label is centered
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        title_container.setLayout(layout)

        title_widget.setDefaultWidget(title_container)
        menu.addAction(title_widget)
        menu.addSeparator()

        for item in os.listdir(self.folder_path):
            item_path = os.path.join(self.folder_path, item)
            item_name_without_extension = os.path.splitext(item)[0]

            if item.endswith(".lnk"):
                # Checks if the shortcut points to a directory
                if is_link_to_directory(item_path):
                    logging.info(f"link shorcut directory : {item_path}")
                    icon_path = "assets/folder.png"
                else:
                    logging.info(f"link shorcut file : {item_path}")
                    icon_path = "assets/circle.png"  # or any other icon you'd prefer for file shortcuts

            elif os.path.isdir(item_path):
                icon_path = "assets/folder.png"
            else:
                icon_path = "assets/circle.png"

            item_action = QAction( QIcon(icon_path), item_name_without_extension, self)
            item_action.setToolTip(f"Open {item_name_without_extension}")
            item_action.triggered.connect(lambda checked, item=item: self.open_item(item))
            menu.addAction(item_action)

        menu.addSeparator()

        quit_action = QAction(QIcon("assets/exit.png"), "Quit", self)
        quit_action.setToolTip("Close the application")
        quit_action.triggered.connect(app.quit)
        menu.addAction(quit_action)
        return menu



    def eventFilter(self, source, event):
        if (event.type() == QEvent.Type.Close and isinstance(source, QMenu)):
            # Reset icon and menu_visible flag
            self.icon_state = 0
            self.tray_icon.setIcon(QIcon(self.icons[self.icon_state]))
            self.menu_visible = False
            # Clearing the context menu for good measure
            self.tray_icon.setContextMenu(None)
        return super(SystemTrayApp, self).eventFilter(source, event)



    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Toggle icon
            self.icon_state = 0 if self.menu_visible else 1
            self.tray_icon.setIcon(QIcon(self.icons[self.icon_state]))

            # Toggle context menu
            if self.menu_visible:
                self.tray_icon.setContextMenu(None)
                self.menu_visible = False
            else:
                menu = self.build_tray_menu()
                self.tray_icon.setContextMenu(menu)

                # Adjusting the position to make the context menu popup above the tray icon
                menu_height = menu.sizeHint().height()
                x_position = self.tray_icon.geometry().x()
                y_position = self.tray_icon.geometry().y() - menu_height
                menu.popup(QPoint(x_position, y_position))
                self.menu_visible = True

    def open_item(self, item):
        try:
            os.startfile(os.path.join(self.folder_path, item))
        except Exception as e:
            logging.error("Error in open_item:", e)


if __name__ == "__main__":
    app = QApplication([])
    logging.info("///// Init /////")
    window = SystemTrayApp("D:\@Portable\[EXTRAFILES]\[shortcuts]")
    sys.exit(app.exec())
