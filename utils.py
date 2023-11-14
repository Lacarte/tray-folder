import sys
import os
import win32com.client


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Use the directory of the script file as the base path
        base_path = os.path.dirname(os.path.abspath(__file__))
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