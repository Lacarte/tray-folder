import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt, QPoint, QEvent
from PyQt5.QtWidgets import QWidgetAction, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QWidget

import os


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
        
        # Creating a custom widget for the title
        title_container = QWidget()
        layout = QVBoxLayout()
        label = QLabel("TRAYFOLDER")
        
        # Adjusting font size and centering text
        label.setStyleSheet("background-color: transparent; color: #EEE; padding: 2px; font-size: 14px;")
        label.setAlignment(Qt.AlignCenter)  # This ensures the label is centered
        
        layout.addWidget(label)
        title_container.setLayout(layout)
        
        title_widget.setDefaultWidget(title_container)
        menu.addAction(title_widget)
        menu.addSeparator()

        for item in os.listdir(self.folder_path):
            item_name_without_extension = os.path.splitext(item)[0]
            item_action = QAction(QIcon("assets/circle.png"), item_name_without_extension, self) # Example with an icon for each file
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
        if (event.type() == QEvent.Close and isinstance(source, QMenu)):
            print("Context menu closed!")
            # Reset icon and menu_visible flag
            self.icon_state = 0 
            self.tray_icon.setIcon(QIcon(self.icons[self.icon_state]))
            self.menu_visible = False
            self.tray_icon.setContextMenu(None)  # Clearing the context menu for good measure
        return super(SystemTrayApp, self).eventFilter(source, event)
    


    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
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
            print("Error in open_item:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemTrayApp("D:\@Portable\[EXTRAFILES]\[shortcuts]")
    sys.exit(app.exec_())
