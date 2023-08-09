import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt, QPoint, QEvent


import os

class CustomMenu(QMenu):
  
    def __init__(self, parent, icons, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.icons = icons

    def hideEvent(self, event):
        # Toggle the icon when the menu is closed
        # self.parent.icon_state = 0
        # self.parent.tray_icon.setIcon(QIcon(self.icons[self.parent.icon_state]))     
        # self.menu_visible = False
        super().hideEvent(event)


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

        # Add title to the menu
        title_action = QAction("Tray-Folder", self)
        title_action.setEnabled(False)
        menu.addAction(title_action)
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

        self.tray_icon.setContextMenu(menu)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.Close and isinstance(source, QMenu)):
            print("Context menu closed!")
            # We can add more actions here if necessary
            
        return super(SystemTrayApp, self).eventFilter(source, event)    


    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            # Toggle icon
            self.icon_state = 1 - self.icon_state
            self.tray_icon.setIcon(QIcon(self.icons[self.icon_state]))
            
            # Toggle context menu
            if self.menu_visible:
                # Hide menu (there's no direct way to hide, so we'll deactivate it)
                self.tray_icon.setContextMenu(None)
                self.menu_visible = False
                print('clicked')
            else:
                # Show menu
                self.build_tray_menu()

                # Adjusting the position to make the context menu popup above the tray icon
                menu_height = self.tray_icon.contextMenu().sizeHint().height()
                x_position = self.tray_icon.geometry().x()
                y_position = self.tray_icon.geometry().y() - menu_height
                self.tray_icon.contextMenu().popup(QPoint(x_position, y_position))
                
                self.menu_visible = True
        
        

    def open_item(self, item):
        os.startfile(os.path.join(self.folder_path, item))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemTrayApp("D:\@Portable\[EXTRAFILES]\[shortcuts]")
    sys.exit(app.exec_())
