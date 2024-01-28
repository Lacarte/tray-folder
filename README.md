
# tray-folder

  
### To set venv() to the .venv directory 

    python -m venv ./.venv

  
### To activate venv 

    .venv\Scripts\activate.bat

  

### To desactivate venv

    .venv\Scripts\desactivate.bat

  
### To backup libraries
#### Only top dependencies 
    pip install pipdeptree
     
    pipdeptree -f --warn silence | findstr  /r  "^[a-zA-Z0-9\-]" > requirements.txt
  
    pipdeptree --warn silence --freeze  --warn silence | grep -v '^\s' > requirements.txt


### To install libraries

    pip install -r requirements.txt


### To convert as executable
pip install pyinstaller


# Python Code Explanation: System Tray Application

This script is a Python application that displays a system tray icon and its associated menu. The primary purpose of this application is to show folder content in a context menu from the system tray.

## Code Overview

### Importing Libraries

The code starts with importing necessary libraries:
- `sys`: for accessing the interpreter variables.
- `os`: for file and directory-related operations.
- `datetime`: to obtain the current date for logging purposes.
- `logging`: for logging different events or messages.
- `link_checker`: a custom module to check if a link points to a directory.
- `PyQt6`: a set of Python bindings for The Qt Company’s Qt application framework.

### Logging Setup

A 'logs' directory is created (if it doesn’t exist), and a log file named with the current date is set up.

### `SystemTrayApp` Class

This class represents the main application window. It includes:

- `__init__`: Initializes the app with an associated folder path.
  - Sets up the tray icon.
  - Builds and displays the tray menu.
- `build_tray_menu`: Constructs the tray menu using items from the given folder path.
  - Checks if an item is a directory, a file, or a shortcut, and assigns an appropriate icon to each.
- `eventFilter`: Overridden method to change the tray icon when the context menu closes.
- `on_tray_icon_activated`: Toggles the visibility of the context menu when the tray icon is clicked.
- `open_item`: Opens the selected item from the context menu using the default application.

### Main Execution

The `if __name__ == "__main__":` block initializes the `QApplication`, sets up the logging, and starts the `SystemTrayApp`.

---

## Key Features

1. **System Tray Icon**: The app creates an icon in the system tray which users can interact with. It also toggles the icon based on the visibility of the context menu.
2. **Context Menu**: When the tray icon is clicked, a context menu is shown. This menu displays the content of a specific folder, allowing users to see the items inside.
3. **Styling**: The context menu has been styled using CSS.
4. **Shortcuts Handling**: The app checks if any of the items in the folder are shortcuts. If they are, and they point to directories, they are treated differently.
5. **Error Handling and Logging**: The app logs events and potential issues, making debugging easier.

---

## How It Works

1. **Initialization**: When the app starts, it initializes the system tray icon and hides the main window since it operates from the system tray.
2. **Tray Icon Activation**: Upon clicking the tray icon, the associated context menu is toggled.
3. **Building the Menu**: The menu is dynamically built based on the contents of the specified folder. Each item in the folder is checked:
   - If it's a `.lnk` (shortcut) and points to a directory, it gets a folder icon.
   - If it's a directory, it gets a folder icon.
   - Otherwise, it gets a file icon.
4. **Opening Items**: When a menu item is clicked, the app attempts to open the item using the system's default application.
5. **Exiting the App**: A quit option is provided in the menu to close the application.

---

This code is a comprehensive example of building a system tray application using PyQt6. The application provides a handy way to access the contents of a particular folder directly from the system tray, making it a great utility for quick access to frequently used files or directories.
