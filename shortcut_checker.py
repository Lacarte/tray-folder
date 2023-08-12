import os
import win32com.client

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
