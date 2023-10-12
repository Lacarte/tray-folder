import sys
import os
import subprocess
import win32com.client
from datetime import datetime
import logging
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow
from PyQt6.QtWidgets import QLabel, QWidgetAction, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt, QEvent
from functools import partial


# Create the "logs" directory if it doesn't exist
try:
    if not os.path.exists("logs"):
        os.makedirs("logs")
except Exception as e:
    print("Error creating 'logs' directory:", e)

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


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def resolve_link(lnk_path):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(lnk_path)
        return shortcut.Targetpath
    except Exception:

        return None


def is_link_broken(lnk_path):
    target_path = resolve_link(lnk_path)
    return target_path is None or not os.path.exists(target_path)


def is_link_to_directory(lnk_path):
    target_path = resolve_link(lnk_path)
    return os.path.isdir(target_path)


# Example
# lnk_file = r"C:\path\to\your\shortcut.lnk"
# print(is_link_to_directory(lnk_file))

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
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(resource_path(self.icons[self.icon_state])))
            self.tray_icon.activated.connect(self.on_tray_icon_activated)
            self.build_tray_menu()
            self.tray_icon.show()

        except Exception as e:
            logging.error("Error initializing tray icon:", e)

    def build_tray_menu(self):
        menu = QMenu()
        menu.installEventFilter(self)

        # Apply CSS Styling to Menu
        menu.setStyleSheet(
        """
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
        label.setStyleSheet(
            "background-color: transparent; color: #EEE; padding: 1px; font-size: 12px;")
        # This ensures the label is centered
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        title_container.setLayout(layout)

        title_widget.setDefaultWidget(title_container)
        menu.addAction(title_widget)
        menu.addSeparator()
        logging.info(f"//scanning directory {self.folder_path}")
        try:
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                item_name_without_extension = os.path.splitext(item)[0]

                if item.endswith(".lnk"):
                    # Checks if the shortcut points to a directory
                    if is_link_to_directory(resource_path(item_path)):
                        logging.info(f"link shorcut directory : {item_path}")
                        icon_path = "assets/folder.png"  # or any other icon you'd prefer for file shortcuts
                    else:
                        if is_link_broken(resource_path(item_path)):
                            logging.info(f"broken shorcut file : {item_path}")
                            icon_path = "assets/broken_shortcut.png"
                        else:
                            logging.info(f"link shorcut file : {item_path}")
                            icon_path = "assets/circle.png"  # or any other icon you'd prefer for file shortcuts

                elif os.path.isdir(resource_path(item_path)):
                    logging.info(f"real directory not file : {item_path}")
                    icon_path = "assets/folder.png"
                else:
                    logging.info(f"real file : {item_path}")
                    icon_path = "assets/circle.png"

                item_action = QAction(QIcon(resource_path(icon_path)), item_name_without_extension, self)
                item_action.setToolTip(f"Open {item_name_without_extension}")
                item_action.triggered.connect(partial(self.open_item, item))
                menu.addAction(item_action)
            menu.addSeparator()
        except Exception as e:
            logging.error(
                f"Error listing items in directory {self.folder_path}:", e)

        quit_action = QAction(QIcon(resource_path("assets/exit.png")), "Quit", self)
        quit_action.setToolTip("Close the application")
        quit_action.triggered.connect(app.quit)
        menu.addAction(quit_action)
        return menu


    def eventFilter(self, source, event):
        if (event.type() == QEvent.Type.Close and isinstance(source, QMenu)):
            # Reset icon and menu_visible flag
            self.icon_state = 0
            self.tray_icon.setIcon(QIcon(resource_path(self.icons[self.icon_state])))
            self.menu_visible = False
            # Clearing the context menu for good measure
            self.tray_icon.setContextMenu(None)
        return super(SystemTrayApp, self).eventFilter(source, event)


    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Toggle icon
            self.icon_state = 0 if self.menu_visible else 1
            self.tray_icon.setIcon(QIcon(resource_path(self.icons[self.icon_state])))

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
        logging.info(f"before opening the item")
        try:
            logging.info(f"opening item : {os.path.join(self.folder_path, item)}")
            subprocess.Popen(['explorer', os.path.join(self.folder_path, item)])
        except Exception as e:
            logging.error(f"Error opening item {item}:", e)


if __name__ == "__main__":
    logging.info("... Init ...")
    app = QApplication([])
    # Ensure app doesn't prematurely exit
    app.setQuitOnLastWindowClosed(False)

    # Specify the path
    folder_path = "D:\\@Portables\\[EXTRAFILES]\\[shortcuts]"

    # Check if the directory exists
    if not os.path.exists(folder_path):
        logging.error(f"Directory not found: {folder_path} , Please fix or update...")
    else:
        try:
            window = SystemTrayApp(folder_path)
            sys.exit(app.exec())
        except Exception as e:
            logging.error("Error initializing application:", e)
