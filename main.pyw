import sys
import os
from datetime import datetime
import logging
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow
from PyQt6.QtWidgets import QLabel, QWidgetAction, QWidget
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHBoxLayout
import configparser
from utils import resource_path, is_link_broken, is_link_to_directory


def setup_logging():
    logs_path = create_directory("logs")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(logs_path, f"log-{datetime.now().strftime('%Y-%m-%d')}.log"), mode="w"),
            logging.StreamHandler(),
        ],
    )

def create_directory(dir_name):
    try:
        path = resource_path(dir_name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    except Exception as e:
        logging.error(f"Error creating '{dir_name}' directory: {e}")
        sys.exit(1)

def get_folder_path_from_config():
    config = configparser.ConfigParser()
    config_path = resource_path("config.ini")
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.ini file not found.")

    config.read(config_path)
    return config.get('Settings', 'folder_path')

class SystemTrayApp(QMainWindow):

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.icon_state = 0
        self.menu_visible = False
        self.icons = ["assets/up.png", "assets/up-open.png"]

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

        title_widget = QWidgetAction(self)
        title_widget.setDisabled(True)

        title_container = QWidget()
        layout = QHBoxLayout()  # Using QHBoxLayout for horizontal layout

        layout.addStretch(1)  # Add stretch before the label to push it towards center

        label = QLabel("TrayFolder")
        label.setStyleSheet("background-color: transparent; color: white; padding: 1px; font-size: 12px;")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)  # Set alignment to center

        layout.addStretch(1)  # Add stretch after the label to maintain center alignment

        title_container.setLayout(layout)
        title_widget.setDefaultWidget(title_container)
        menu.addAction(title_widget)

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
                else:
                    item_name_without_extension = os.path.splitext(item)[0]

                    # Initialize variable to track if the link is broken
                    is_broken_link = False

                    if item.endswith(".lnk"):
                        # Check if the shortcut points to a directory or if it's broken
                        if is_link_to_directory(resource_path(item_path)):
                            icon_path = "assets/folder.png"
                        else:
                            if is_link_broken(resource_path(item_path)):
                                is_broken_link = True
                                icon_path = "assets/broken_shortcut.png"
                            else:
                                icon_path = "assets/circle.png"

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
                    
                    # If the link is broken, disable the action
                    if is_broken_link:
                        item_action.setDisabled(True)
                    else:
                        item_action.triggered.connect(make_item_action_triggered(item))
                    menu.addAction(item_action)
                menu.addSeparator()
                
        except Exception as e:
            logging.error(
                f"Error listing items in directory {self.folder_path}:", e)


     # Add custom folder path action before Quit action
        folder_name = os.path.basename(self.folder_path)
        folder_icon_path = "assets/folder.png"
        folder_action = QAction(QIcon(resource_path(folder_icon_path)), folder_name, self)
        folder_action.setToolTip(f"Open {self.folder_path}")
        folder_action.triggered.connect(lambda: self.open_item(folder_name))
        menu.addAction(folder_action)

        menu.addSeparator()

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

        item_path = os.path.join(self.folder_path, item)
        logging.info(f"before opening the item")
        
        if item == os.path.basename(self.folder_path):
            item_path = self.folder_path
        
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
    setup_logging()
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    try:
        folder_path = get_folder_path_from_config()
        if not os.path.exists(folder_path):
            logging.error(f"Directory {folder_path} not found.")
            sys.exit(1)

        window = SystemTrayApp(folder_path)
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error in main: {e}")
        sys.exit(1)
