import os
import win32com.client

def resolve_link(lnk_path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(lnk_path)
    return shortcut.Targetpath

def is_link_to_directory(lnk_path):
    target_path = resolve_link(lnk_path)
    return os.path.isdir(target_path)

# Example
# lnk_file = r"C:\path\to\your\shortcut.lnk"
# print(is_link_to_directory(lnk_file))
