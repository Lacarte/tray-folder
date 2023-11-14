import sys
import os
import subprocess
from datetime import datetime
import logging
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow
from PyQt6.QtWidgets import QLabel, QWidgetAction, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QPixmap
from functools import partial
from PyQt6.QtWidgets import QHBoxLayout
import configparser
from utils import resource_path
from utils import is_link_broken
from utils import is_link_to_directory

# Create the "logs" directory if it doesn't exist
try:
    logs_path = resource_path("logs")
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
except Exception as e:
    print("Error creating 'logs' directory:", e)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(logs_path, f"log-{datetime.now().strftime('%Y-%m-%d')}.log"),
            mode="w",
        ),
        logging.StreamHandler(),
    ],
)


def get_folder_path_from_config():
    config = configparser.ConfigParser()
    config_path = resource_path("config.ini")

    # Debugging: Print or log the path being checked
    print(f"Looking for config.ini at: {config_path}")  # or use logging.info()

    if not os.path.exists(config_path):
        raise FileNotFoundError("Oops! I couldn't find the 'config.ini' file. Did a kitten play with it? 🐱")

    config.read(config_path)
    # Rest of your code...
    folder_path = config['Settings']['folder_path']
    print(f"Retrieved folder path: {folder_path}")
    return folder_path


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

        title_widget = QWidgetAction(self)
        # Disabling the action to make it unclickable
        title_widget.setDisabled(True)

        # Creating a custom widget for the title
        title_container = QWidget()
        layout = QHBoxLayout()  # Use QHBoxLayout for horizontal layout

        # Adding the text
        label = QLabel("TrayFolder")
        label.setStyleSheet("background-color: transparent; color: white; padding: 1px; font-size: 12px;")
        layout.addWidget(label)

        # Adding the icon to the right
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/title_icon.png"))
        icon_label.setPixmap(icon_pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio)) # Adjust the size as needed
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignRight)

        title_container.setLayout(layout)
        title_widget.setDefaultWidget(title_container)
        menu.addAction(title_widget)

        menu.addSeparator()
        logging.info(f"//scanning directory {self.folder_path}")
        try:
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if not os.path.exists(item_path):
                    logging.info(f"item_path no exist {item_path}")
                else :
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
                        logging.info(f"is real directory not a file : {item_path}")
                        icon_path = "assets/folder.png"
                    else:
                        logging.info(f"real file : {item_path}")
                        icon_path = "assets/circle.png"

                    def make_item_action_triggered(item_name):
                        def item_action_triggered():
                            self.open_item(item_name)
                        return item_action_triggered

                    item_action = QAction(QIcon(resource_path(icon_path)), item_name_without_extension, self)
                    item_action.setToolTip(f"Open {item_name_without_extension}")
                    item_action.triggered.connect(make_item_action_triggered(item))
                    logging.info(f"item_action : {item_action}")
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
        # Check if the source is the menu and the event is a close event
        if isinstance(source, QMenu) and event.type() == QEvent.Type.Close:
            # Reset icon and menu_visible flag only if the menu is currently visible
            if self.menu_visible:
                self.icon_state = 0
                self.tray_icon.setIcon(QIcon(resource_path(self.icons[self.icon_state])))
                self.menu_visible = False
            return True  # Indicate that the event was handled
        # For all other cases, call the base class implementation
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
        item_path = os.path.join(self.folder_path, item)
        print(f"Attempting to open: {item_path}")  # or use logging.info()
     
        if not os.path.exists(item_path):
            logging.error(f"{item_path} does not exist!")
            return

        if not os.path.isfile(item_path) and not os.path.isdir(item_path):
            logging.error(f"{item_path} is not a valid file or folder")  
            return
  
        try:
            self.icon_state = 0
            self.tray_icon.setIcon(QIcon(resource_path(self.icons[self.icon_state])))
            self.menu_visible = False
            # Clearing the context menu for good measure
            self.tray_icon.setContextMenu(None)
            # Opening file or folder
            # subprocess.Popen(['explorer', item_path])
            full_path = os.path.abspath(item_path)
            os.startfile(full_path)

        except Exception as e:
         logging.error("Error opening path:", e)


if __name__ == "__main__":
    logging.info("... Init ...")
    app = QApplication([])
    # Ensure app doesn't prematurely exit
    app.setQuitOnLastWindowClosed(False)

    folder_path = get_folder_path_from_config()
    logging.info(f"Shortcut {folder_path}")
    # Check if the directory exists
    if not os.path.exists(folder_path):
        logging.error(f"Directory {folder_path} not found, please fix or update SHORTCUT ...")
    else:
        try:
            window = SystemTrayApp(folder_path)
            sys.exit(app.exec())
        except Exception as e:
            logging.error("Error initializing application:", e)
