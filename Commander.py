import os
import sys
import time
import json
import shutil
import socket
import hashlib
import getpass
import subprocess
import platform
import tempfile
import ctypes
import threading
from pathlib import Path
from datetime import datetime

# ============================================================
# COMMANDER v2.0
# Personal PC Utility Suite
# ============================================================

VERSION = "2.0"

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "commander_config.json"
NOTES_FILE = BASE_DIR / "commander_notes.txt"
CLIPBOARD_FILE = BASE_DIR / "clipboard_history.json"
VAULT_DIR = BASE_DIR / ".commander_vault"
VAULT_CONFIG = BASE_DIR / ".commander_vault.json"

DEFAULT_CONFIG = {
    "theme": "blue",
    "confirm_delete": True,
    "search_hidden": False,
    "default_drive": str(Path.home().anchor),
    "show_status": True
}


# ============================================================
# COLORS
# ============================================================

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"


def enable_ansi():
    """Enable ANSI colors on Windows."""
    if os.name == "nt":
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(
                kernel32.GetStdHandle(-11),
                7
            )
        except Exception:
            pass


enable_ansi()


# ============================================================
# CONFIG
# ============================================================

def load_config():
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        for key, value in DEFAULT_CONFIG.items():
            config.setdefault(key, value)

        return config

    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception:
        pass


CONFIG = load_config()


# ============================================================
# GENERAL UI
# ============================================================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause(message="Press ENTER to continue..."):
    input(f"\n{C.DIM}{message}{C.RESET}")


def title(text):
    clear()

    width = 58

    print(C.BLUE + C.BOLD)
    print("╔" + "═" * width + "╗")
    print("║" + text.center(width) + "║")
    print("╚" + "═" * width + "╝")
    print(C.RESET)


def section(text):
    print()
    print(C.CYAN + C.BOLD + f"── {text} " + "─" * max(2, 50 - len(text)) + C.RESET)


def success(text):
    print(C.GREEN + "✓ " + text + C.RESET)


def error(text):
    print(C.RED + "✗ " + text + C.RESET)


def warning(text):
    print(C.YELLOW + "⚠ " + text + C.RESET)


def info(text):
    print(C.CYAN + "ℹ " + text + C.RESET)


def human_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(size)

    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def human_time(seconds):
    seconds = int(seconds)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h:
        return f"{h}h {m}m {s}s"

    if m:
        return f"{m}m {s}s"

    return f"{s}s"


def progress_bar(current, total, width=30):
    if total <= 0:
        return "[" + " " * width + "]"

    ratio = min(1, current / total)
    filled = int(width * ratio)

    return (
        "["
        + "█" * filled
        + "░" * (width - filled)
        + "]"
        + f" {ratio * 100:5.1f}%"
    )


# ============================================================
# STATUS BAR
# ============================================================

def get_memory():
    try:
        import psutil

        mem = psutil.virtual_memory()
        return mem.percent

    except Exception:
        return None


def get_cpu():
    try:
        import psutil

        return psutil.cpu_percent(interval=0.1)

    except Exception:
        return None


def get_disk():
    try:
        drive = Path.home().anchor
        usage = shutil.disk_usage(drive)

        return usage.used / usage.total * 100

    except Exception:
        return None


def status_bar():
    if not CONFIG.get("show_status", True):
        return

    cpu = get_cpu()
    ram = get_memory()
    disk = get_disk()

    cpu_text = f"{cpu:.0f}%" if cpu is not None else "N/A"
    ram_text = f"{ram:.0f}%" if ram is not None else "N/A"
    disk_text = f"{disk:.0f}%" if disk is not None else "N/A"

    print(
        C.DIM
        + f"CPU {cpu_text}   RAM {ram_text}   DISK {disk_text}"
        + C.RESET
    )


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():
    while True:
        title("COMMANDER v2.0")

        print(C.CYAN + "Personal PC Utility Suite" + C.RESET)
        print()

        print("  1  🔎  WhereIs")
        print("  2  💾  SpaceHog")
        print("  3  🔐  LockBox")
        print("  4  🧪  WhatIsThis")
        print("  5  ⏱️   Focus")
        print("  6  ⚡  Command Bar")
        print("  7  📊  System Monitor")
        print("  8  🧹  QuickClean")
        print("  9  📁  File Manager")
        print(" 10  🌐  Network")
        print(" 11  🔧  Windows Tools")
        print(" 12  📋  Clipboard Manager")
        print(" 13  📝  Notes")
        print(" 14  ⚙️   Settings")
        print(" 15  ❓  Help")
        print()
        print("  Q  🚪  Exit")

        print()
        status_bar()

        choice = input(
            f"\n{C.BOLD}COMMANDER > {C.RESET}"
        ).strip().lower()

        if choice == "1":
            where_is()

        elif choice == "2":
            space_hog()

        elif choice == "3":
            lockbox()

        elif choice == "4":
            what_is_this()

        elif choice == "5":
            focus()

        elif choice == "6":
            command_bar()

        elif choice == "7":
            system_monitor()

        elif choice == "8":
            quick_clean()

        elif choice == "9":
            file_manager()

        elif choice == "10":
            network_tools()

        elif choice == "11":
            windows_tools()

        elif choice == "12":
            clipboard_manager()

        elif choice == "13":
            notes()

        elif choice == "14":
            settings()

        elif choice == "15":
            help_menu()

        elif choice == "q":
            clear()
            print(C.CYAN + C.BOLD)
            print("COMMANDER shutting down...")
            print(C.RESET)
            time.sleep(0.7)
            break

        else:
            warning("Invalid option.")
            time.sleep(0.8)


# ============================================================
# 1. WHEREIS
# ============================================================

def get_windows_drives():
    drives = []

    if os.name == "nt":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"

            if os.path.exists(drive):
                drives.append(drive)

    else:
        drives.append("/")

    return drives


def where_is():
    title("WHEREIS — WHOLE PC SEARCH")

    print(
        C.DIM
        + "Searches your available drives for files and folders."
        + C.RESET
    )

    print()

    query = input("Search for: ").strip()

    if not query:
        return

    extension = input(
        "Extension filter (optional, e.g. .pdf): "
    ).strip()

    print()

    drives = get_windows_drives()

    print(
        C.CYAN
        + "Drives to scan:"
        + C.RESET
    )

    for drive in drives:
        print("  •", drive)

    print()

    input("Press ENTER to start searching...")

    results = []
    scanned = 0
    start = time.time()

    for drive in drives:

        for root, dirs, files in os.walk(
            drive,
            topdown=True,
            onerror=lambda e: None
        ):

            # Skip inaccessible/system locations where possible
            dirs[:] = [
                d for d in dirs
                if CONFIG.get("search_hidden", False)
                or not d.startswith("$")
            ]

            try:
                names = files + dirs
            except Exception:
                continue

            for name in names:

                scanned += 1

                if query.lower() not in name.lower():
                    continue

                if extension:
                    if not name.lower().endswith(extension.lower()):
                        continue

                full_path = os.path.join(root, name)

                results.append(full_path)

                print(
                    C.GREEN
                    + f"[{len(results)}] "
                    + C.RESET
                    + full_path
                )

                if len(results) >= 500:
                    warning("Maximum of 500 results reached.")
                    break

            if len(results) >= 500:
                break

        if len(results) >= 500:
            break

    elapsed = time.time() - start

    print()
    print(
        C.CYAN
        + f"Search complete: {len(results)} result(s)"
        + C.RESET
    )

    print(
        C.DIM
        + f"Scanned {scanned:,} filesystem entries in {elapsed:.1f}s"
        + C.RESET
    )

    if results:

        print()
        choice = input(
            "Enter result number to open, or ENTER to return: "
        ).strip()

        if choice.isdigit():

            index = int(choice) - 1

            if 0 <= index < len(results):
                open_path(results[index])

    pause()


# ============================================================
# 2. SPACEHOG
# ============================================================

def get_directory_size(path):
    total = 0

    try:

        for root, dirs, files in os.walk(
            path,
            topdown=True,
            onerror=lambda e: None
        ):

            for file in files:

                try:
                    total += os.path.getsize(
                        os.path.join(root, file)
                    )

                except Exception:
                    pass

    except Exception:
        pass

    return total


def scan_space(path):
    entries = []

    try:

        for item in os.scandir(path):

            try:

                if item.is_file(follow_symlinks=False):
                    size = item.stat(
                        follow_symlinks=False
                    ).st_size

                elif item.is_dir(
                    follow_symlinks=False
                ):
                    size = get_directory_size(
                        item.path
                    )

                else:
                    continue

                entries.append(
                    (item.path, size, item.is_dir())
                )

            except Exception:
                continue

    except Exception:
        pass

    entries.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return entries


def space_hog():
    title("SPACEHOG — STORAGE ANALYZER")

    print(
        C.DIM
        + "Find what's taking up your storage."
        + C.RESET
    )

    print()

    drive = input(
        f"Drive/folder [{Path.home().anchor}]: "
    ).strip()

    if not drive:
        drive = Path.home().anchor

    drive = os.path.abspath(drive)

    if not os.path.exists(drive):
        error("Location does not exist.")
        pause()
        return

    print()
    print("Scanning storage...")
    print("Large folders may take a while.")

    start = time.time()

    entries = scan_space(drive)

    elapsed = time.time() - start

    if not entries:
        warning("Nothing could be scanned.")
        pause()
        return

    while True:

        title("SPACEHOG — STORAGE")

        print(
            C.DIM
            + f"Location: {drive}"
            + C.RESET
        )

        print(
            C.DIM
            + f"Scanned in {elapsed:.1f}s"
            + C.RESET
        )

        print()

        for i, (path, size, is_dir) in enumerate(
            entries[:50],
            start=1
        ):

            icon = "📁" if is_dir else "📄"

            print(
                f"{i:2}. {icon} "
                f"{human_size(size):>12}  "
                f"{path}"
            )

        print()
        print("D  Delete")
        print("O  Open")
        print("R  Rescan")
        print("Q  Back")

        choice = input(
            f"\n{C.BOLD}SPACEHOG > {C.RESET}"
        ).strip().lower()

        if choice == "q":
            return

        if choice == "r":
            entries = scan_space(drive)
            continue

        if choice in ("d", "o"):

            number = input("Item number: ").strip()

            if not number.isdigit():
                continue

            index = int(number) - 1

            if not 0 <= index < len(entries[:50]):
                continue

            path, size, is_dir = entries[index]

            if choice == "o":
                open_path(path)

            else:
                delete_path(path)

            pause()


# ============================================================
# 3. LOCKBOX
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def lockbox():
    title("LOCKBOX — PRIVATE VAULT")

    print(
        C.DIM
        + "A simple local vault for files."
        + C.RESET
    )

    print()

    if not VAULT_CONFIG.exists():

        print("No LockBox exists yet.")

        password = getpass.getpass(
            "Create password: "
        )

        confirm = getpass.getpass(
            "Confirm password: "
        )

        if password != confirm:
            error("Passwords do not match.")
            pause()
            return

        with open(VAULT_CONFIG, "w") as f:
            json.dump(
                {"password": hash_password(password)},
                f
            )

        VAULT_DIR.mkdir(exist_ok=True)

        success("LockBox created.")

    password = getpass.getpass(
        "LockBox password: "
    )

    try:
        with open(VAULT_CONFIG) as f:
            data = json.load(f)

    except Exception:
        error("LockBox configuration is damaged.")
        pause()
        return

    if hash_password(password) != data["password"]:
        error("Incorrect password.")
        pause()
        return

    VAULT_DIR.mkdir(exist_ok=True)

    while True:

        title("LOCKBOX")

        print("1  Add file")
        print("2  List files")
        print("3  Extract file")
        print("4  Delete file")
        print("Q  Back")

        choice = input(
            f"\n{C.BOLD}LOCKBOX > {C.RESET}"
        ).strip().lower()

        if choice == "q":
            return

        if choice == "1":

            source = input("File to add: ").strip()

            if not os.path.isfile(source):
                error("File not found.")
                pause()
                continue

            destination = VAULT_DIR / Path(source).name

            try:
                shutil.copy2(source, destination)
                success("File added to LockBox.")

            except Exception as e:
                error(str(e))

            pause()

        elif choice == "2":

            files = list(VAULT_DIR.iterdir())

            if not files:
                info("LockBox is empty.")

            else:
                for file in files:
                    print(
                        f"• {file.name} "
                        f"({human_size(file.stat().st_size)})"
                    )

            pause()

        elif choice == "3":

            name = input(
                "File name to extract: "
            ).strip()

            source = VAULT_DIR / name

            if not source.exists():
                error("File not found.")
                pause()
                continue

            destination = input(
                "Destination folder: "
            ).strip()

            if not destination:
                destination = str(Path.home() / "Downloads")

            try:
                shutil.copy2(
                    source,
                    Path(destination) / source.name
                )

                success("File extracted.")

            except Exception as e:
                error(str(e))

            pause()

        elif choice == "4":

            name = input(
                "File to delete: "
            ).strip()

            target = VAULT_DIR / name

            if target.exists():
                delete_path(target)

            pause()


# ============================================================
# 4. WHAT IS THIS
# ============================================================

def what_is_this():
    title("WHATISTHIS — FILE INFORMATION")

    path = input("File/folder path: ").strip()

    path = os.path.abspath(
        os.path.expandvars(path)
    )

    if not os.path.exists(path):
        error("Path does not exist.")
        pause()
        return

    p = Path(path)

    try:
        stat = p.stat()

        print()
        print("Name:       ", p.name)
        print("Location:   ", p.parent)
        print("Type:       ", "Folder" if p.is_dir() else "File")
        print("Extension:  ", p.suffix or "None")
        print("Size:       ", human_size(stat.st_size))
        print(
            "Created:    ",
            datetime.fromtimestamp(
                stat.st_ctime
            )
        )
        print(
            "Modified:   ",
            datetime.fromtimestamp(
                stat.st_mtime
            )
        )
        print(
            "Accessed:   ",
            datetime.fromtimestamp(
                stat.st_atime
            )
        )

        if p.is_file():

            try:
                with open(
                    p,
                    "rb"
                ) as f:
                    data = f.read(4096)

                print()
                print(
                    "SHA-256:",
                    hashlib.sha256(data).hexdigest()
                )

            except Exception:
                pass

    except Exception as e:
        error(str(e))

    pause()


# ============================================================
# 5. FOCUS
# ============================================================

def focus():
    title("FOCUS — TIMER")

    print("1  25 minutes")
    print("2  45 minutes")
    print("3  60 minutes")
    print("4  Custom")
    print("Q  Back")

    choice = input(
        f"\n{C.BOLD}FOCUS > {C.RESET}"
    ).strip().lower()

    if choice == "q":
        return

    if choice == "1":
        minutes = 25

    elif choice == "2":
        minutes = 45

    elif choice == "3":
        minutes = 60

    elif choice == "4":

        try:
            minutes = int(
                input("Minutes: ")
            )

        except ValueError:
            return

    else:
        return

    seconds = minutes * 60

    clear()

    print(
        C.CYAN
        + C.BOLD
        + "FOCUS SESSION"
        + C.RESET
    )

    print()

    start = time.time()

    while seconds > 0:

        mins, secs = divmod(seconds, 60)

        print(
            f"\r{C.BOLD}"
            f"{mins:02d}:{secs:02d}"
            f"{C.RESET}",
            end=""
        )

        time.sleep(1)

        seconds -= 1

    print()

    print()
    success("Focus session complete!")

    try:
        if os.name == "nt":
            import winsound

            winsound.Beep(
                1000,
                700
            )

    except Exception:
        pass

    pause()


# ============================================================
# 6. COMMAND BAR
# ============================================================

COMMANDS = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "calc": ["calc.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "paint": ["mspaint.exe"],
    "taskmgr": ["taskmgr.exe"],
    "explorer": ["explorer.exe"],
    "control": ["control.exe"],
}


def command_bar():
    title("COMMAND BAR")

    print(
        C.DIM
        + "Launch programs, folders and commands."
        + C.RESET
    )

    print()
    print("Examples:")
    print("  notepad")
    print("  calculator")
    print("  downloads")
    print("  cmd")
    print("  taskmgr")
    print()

    while True:

        command = input(
            f"{C.BOLD}COMMAND > {C.RESET}"
        ).strip()

        if not command:
            return

        if command.lower() == "exit":
            return

        if command.lower() == "downloads":
            path = Path.home() / "Downloads"

            if path.exists():
                os.startfile(path)
                continue

        if command.lower() in COMMANDS:

            try:
                subprocess.Popen(
                    COMMANDS[command.lower()]
                )

                success("Launched.")

            except Exception as e:
                error(str(e))

            continue

        if os.path.exists(command):

            open_path(command)
            continue

        try:

            subprocess.Popen(
                command,
                shell=True
            )

            success("Command launched.")

        except Exception as e:
            error(str(e))


# ============================================================
# 7. SYSTEM MONITOR
# ============================================================

def system_monitor():
    try:
        import psutil
    except ImportError:

        title("SYSTEM MONITOR")

        warning(
            "System Monitor requires the 'psutil' package."
        )

        print()
        print("Install it with:")
        print()
        print("    py -m pip install psutil")

        pause()
        return

    while True:

        title("SYSTEM MONITOR")

        cpu = psutil.cpu_percent(interval=0.3)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(
            Path.home().anchor
        )

        print(
            "CPU  "
            + progress_bar(cpu, 100)
        )

        print(
            "RAM  "
            + progress_bar(
                memory.percent,
                100
            )
        )

        print(
            "DISK "
            + progress_bar(
                disk.percent,
                100
            )
        )

        print()

        print(
            f"CPU cores:       {psutil.cpu_count(logical=True)}"
        )

        print(
            f"RAM total:       {human_size(memory.total)}"
        )

        print(
            f"RAM available:   {human_size(memory.available)}"
        )

        print(
            f"Disk free:       {human_size(disk.free)}"
        )

        print(
            f"Boot time:       "
            f"{datetime.fromtimestamp(psutil.boot_time())}"
        )

        print()

        print("Top processes:")

        processes = []

        for proc in psutil.process_iter(
            ["name", "memory_info"]
        ):

            try:

                mem = proc.info[
                    "memory_info"
                ].rss

                processes.append(
                    (
                        proc.info["name"] or "?",
                        mem
                    )
                )

            except Exception:
                pass

        processes.sort(
            key=lambda x: x[1],
            reverse=True
        )

        for name, memory_used in processes[:10]:

            print(
                f"  {name[:30]:30} "
                f"{human_size(memory_used)}"
            )

        print()
        print("R  Refresh")
        print("Q  Back")

        choice = input(
            f"\n{C.BOLD}MONITOR > {C.RESET}"
        ).strip().lower()

        if choice == "q":
            return


# ============================================================
# 8. QUICK CLEAN
# ============================================================

def quick_clean():
    title("QUICKCLEAN")

    print(
        "Temporary files and common cleanup locations:"
    )

    locations = []

    temp = Path(tempfile.gettempdir())

    if temp.exists():
        locations.append(
            ("Temporary Files", temp)
        )

    downloads = Path.home() / "Downloads"

    if downloads.exists():
        locations.append(
            ("Downloads", downloads)
        )

    recycle = None

    if os.name == "nt":
        recycle = Path(
            os.environ.get(
                "SystemDrive",
                "C:"
            ) + "\\$Recycle.Bin"
        )

        if recycle.exists():
            locations.append(
                ("Recycle Bin", recycle)
            )

    for i, (name, path) in enumerate(
        locations,
        1
    ):

        print(
            f"{i}. {name}"
        )

        print(
            f"   {path}"
        )

    print()
    print(
        C.YELLOW
        + "QuickClean does not automatically delete anything."
        + C.RESET
    )

    choice = input(
        "\nSelect location, or Q to return: "
    ).strip().lower()

    if choice == "q":
        return

    if not choice.isdigit():
        return

    index = int(choice) - 1

    if not 0 <= index < len(locations):
        return

    name, path = locations[index]

    size = get_directory_size(path)

    print()
    print(
        f"{name} contains approximately "
        f"{human_size(size)}."
    )

    confirm = input(
        "Delete contents? Type DELETE: "
    )

    if confirm != "DELETE":
        warning("Cancelled.")
        pause()
        return

    deleted = 0

    try:

        for item in path.iterdir():

            try:

                if item.is_dir():
                    shutil.rmtree(item)

                else:
                    item.unlink()

                deleted += 1

            except Exception:
                pass

        success(
            f"Removed {deleted} item(s)."
        )

    except Exception as e:
        error(str(e))

    pause()


# ============================================================
# 9. FILE MANAGER
# ============================================================

def file_manager():
    current = Path(
        CONFIG.get(
            "default_drive",
            Path.home().anchor
        )
    )

    if not current.exists():
        current = Path.home()

    while True:

        title("FILE MANAGER")

        print(
            C.CYAN
            + str(current)
            + C.RESET
        )

        print()

        try:
            items = list(current.iterdir())

            items.sort(
                key=lambda p: (
                    not p.is_dir(),
                    p.name.lower()
                )
            )

        except Exception:
            error("Cannot access this folder.")
            pause()
            return

        for i, item in enumerate(
            items[:100],
            1
        ):

            try:
                if item.is_dir():
                    icon = "📁"
                    size = "<DIR>"

                else:
                    icon = "📄"
                    size = human_size(
                        item.stat().st_size
                    )

            except Exception:
                icon = "?"
                size = "?"

            print(
                f"{i:3}. {icon} "
                f"{size:>12}  {item.name}"
            )

        print()
        print("..  Parent")
        print("N   New folder")
        print("D   Delete")
        print("R   Rename")
        print("O   Open")
        print("Q   Back")

        choice = input(
            f"\n{C.BOLD}FILEMAN > {C.RESET}"
        ).strip()

        if choice.lower() == "q":
            return

        if choice == "..":
            current = current.parent
            continue

        if choice.lower() == "n":

            name = input(
                "Folder name: "
            ).strip()

            if name:
                try:
                    (current / name).mkdir()
                    success("Folder created.")
                except Exception as e:
                    error(str(e))

            continue

        if choice.lower() in (
            "d",
            "r",
            "o"
        ):

            number = input(
                "Item number: "
            ).strip()

            if not number.isdigit():
                continue

            index = int(number) - 1

            if not 0 <= index < min(
                len(items),
                100
            ):
                continue

            target = items[index]

            if choice.lower() == "o":

                if target.is_dir():
                    current = target

                else:
                    open_path(target)

            elif choice.lower() == "d":

                delete_path(target)

            elif choice.lower() == "r":

                new_name = input(
                    "New name: "
                ).strip()

                if new_name:

                    try:
                        target.rename(
                            target.parent / new_name
                        )

                        success("Renamed.")

                    except Exception as e:
                        error(str(e))


# ============================================================
# 10. NETWORK
# ============================================================

def network_tools():
    while True:

        title("NETWORK TOOLS")

        print("1  Connection status")
        print("2  Local IP")
        print("3  Ping")
        print("4  DNS lookup")
        print("Q  Back")

        choice = input(
            f"\n{C.BOLD}NETWORK > {C.RESET}"
        ).strip().lower()

        if choice == "q":
            return

        if choice == "1":

            try:

                socket.create_connection(
                    ("8.8.8.8", 53),
                    timeout=3
                )

                success("Internet connection: ONLINE")

            except Exception:

                error(
                    "Internet connection: OFFLINE"
                )

            pause()

        elif choice == "2":

            try:

                hostname = socket.gethostname()

                ip = socket.gethostbyname(
                    hostname
                )

                print(
                    f"Hostname: {hostname}"
                )

                print(
                    f"Local IP: {ip}"
                )

            except Exception as e:
                error(str(e))

            pause()

        elif choice == "3":

            host = input(
                "Host to ping: "
            ).strip()

            if not host:
                continue

            command = (
                ["ping", "-n", "4", host]
                if os.name == "nt"
                else
                ["ping", "-c", "4", host]
            )

            subprocess.run(
                command
            )

            pause()

        elif choice == "4":

            host = input(
                "Domain: "
            ).strip()

            try:

                addresses = socket.gethostbyname_ex(
                    host
                )

                print()
                print(
                    "Hostname:",
                    addresses[0]
                )

                print(
                    "Addresses:"
                )

                for address in addresses[2]:
                    print(
                        " •",
                        address
                    )

            except Exception as e:
                error(str(e))

            pause()


# ============================================================
# 11. WINDOWS TOOLS
# ============================================================

def windows_tools():
    if os.name != "nt":

        title("WINDOWS TOOLS")

        warning(
            "These tools are designed for Windows."
        )

        pause()
        return

    tools = {
        "1": ("Task Manager", ["taskmgr.exe"]),
        "2": ("Device Manager", ["devmgmt.msc"]),
        "3": ("Disk Management", ["diskmgmt.msc"]),
        "4": ("Services", ["services.msc"]),
        "5": ("Event Viewer", ["eventvwr.msc"]),
        "6": ("System Information", ["msinfo32.exe"]),
        "7": ("Control Panel", ["control.exe"]),
        "8": ("Windows Settings", ["start", "ms-settings:"]),
        "9": ("Command Prompt", ["cmd.exe"]),
        "10": ("PowerShell", ["powershell.exe"])
    }

    while True:

        title("WINDOWS TOOLS")

        for key, (name, _) in tools.items():
            print(f"{key:>2}  {name}")

        print("Q   Back")

        choice = input(
            f"\n{C.BOLD}WINDOWS > {C.RESET}"
        ).strip().lower()

        if choice == "q":
            return

        if choice in tools:

            name, command = tools[choice]

            try:

                subprocess.Popen(
                    command,
                    shell=False
                )

                success(
                    f"Opened {name}."
                )

            except Exception as e:
                error(str(e))

            time.sleep(0.7)


# ============================================================
# 12. CLIPBOARD MANAGER
# ============================================================

def get_clipboard():

    if os.name == "nt":

        try:

            import tkinter as tk

            root = tk.Tk()
            root.withdraw()

            text = root.clipboard_get()

            root.destroy()

            return text

        except Exception:
            return ""

    return ""


def set_clipboard(text):

    if os.name == "nt":

        try:

            import tkinter as tk

            root = tk.Tk()
            root.withdraw()

            root.clipboard_clear()
            root.clipboard_append(text)

            root.update()

            root.destroy()

            return True

        except Exception:
            return False

    return False


def load_clipboard_history():

    if not CLIPBOARD_FILE.exists():
        return []

    try:

        with open(
            CLIPBOARD_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return []


def save_clipboard_history(history):

    try:

        with open(
            CLIPBOARD_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                history[:50],
                f,
                indent=2
            )

    except Exception:
        pass


def clipboard_manager():

    history = load_clipboard_history()

    while True:

        title("CLIPBOARD MANAGER")

        current = get_clipboard()

        if current:

            print(
                C.CYAN
                + "CURRENT CLIPBOARD:"
                + C.RESET
            )

            print(
                current[:500]
            )

        else:

            print(
                C.DIM
                + "Clipboard is empty or unavailable."
                + C.RESET
            )

        print()

        print("1  Save current clipboard")
        print("2  View history")
        print("3  Copy history item")
        print("4  Clear clipboard")
        print("5  Clear history")
        print("Q  Back")

        choice = input(
            f"\n{C.BOLD}CLIPBOARD > {C.RESET}"
        ).strip().lower()

        if choice == "q":
            return

        if choice == "1":

            if current:

                if current not in history:
                    history.insert(
                        0,
                        current
                    )

                history = history[:50]

                save_clipboard_history(
                    history
                )

                success("Saved.")

            pause()

        elif choice == "2":

            if not history:
                info("History is empty.")

            else:

                for i, text in enumerate(
                    history,
                    1
                ):

                    preview = (
                        text.replace(
                            "\n",
                            " "
                        )[:70]
                    )

                    print(
                        f"{i:2}. {preview}"
                    )

            pause()

        elif choice == "3":

            number = input(
                "History number: "
            ).strip()

            if number.isdigit():

                index = int(number) - 1

                if 0 <= index < len(history):

                    if set_clipboard(
                        history[index]
                    ):
                        success(
                            "Copied to clipboard."
                        )
                    else:
                        error(
                            "Could not access clipboard."
                        )

            pause()

        elif choice == "4":

            if set_clipboard(""):
                success(
                    "Clipboard cleared."
                )
            else:
                error(
                    "Could not clear clipboard."
                )

            pause()

        elif choice == "5":

            history.clear()

            save_clipboard_history(
                history
            )

            success("History cleared.")

            pause()


# ============================================================
# 13. NOTES
# ============================================================

def notes():

    while True:

        title("NOTES")

        print("1  View notes")
        print("2  Add note")
        print("3  Clear notes")
        print("Q  Back")

        choice = input(
            f"\n{C.BOLD}NOTES > {C.RESET}"
        ).strip().lower()

        if choice == "q":
            return

        if choice == "1":

            if not NOTES_FILE.exists():

                info("No notes yet.")

            else:

                try:

                    with open(
                        NOTES_FILE,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = f.read()

                    print()
                    print(content)

                except Exception as e:
                    error(str(e))

            pause()

        elif choice == "2":

            print(
                "Enter your note."
            )

            print(
                "Type END on a new line when finished."
            )

            lines = []

            while True:

                line = input()

                if line == "END":
                    break

                lines.append(line)

            if lines:

                try:

                    with open(
                        NOTES_FILE,
                        "a",
                        encoding="utf-8"
                    ) as f:

                        f.write(
                            "\n"
                            + datetime.now().strftime(
                                "[%Y-%m-%d %H:%M]"
                            )
                            + "\n"
                        )

                        f.write(
                            "\n".join(lines)
                        )

                        f.write("\n")

                    success("Note saved.")

                except Exception as e:
                    error(str(e))

            pause()

        elif choice == "3":

            confirm = input(
                "Type CLEAR to delete all notes: "
            )

            if confirm == "CLEAR":

                try:
                    NOTES_FILE.unlink(
                        missing_ok=True
                    )

                    success(
                        "Notes cleared."
                    )

                except Exception as e:
                    error(str(e))

            pause()


# ============================================================
# 14. SETTINGS
# ============================================================

def settings():

    global CONFIG

    while True:

        title("COMMANDER SETTINGS")

        print(
            f"1  Theme              {CONFIG['theme']}"
        )

        print(
            f"2  Confirm Deletes    "
            f"{CONFIG['confirm_delete']}"
        )

        print(
            f"3  Search Hidden      "
            f"{CONFIG['search_hidden']}"
        )

        print(
            f"4  Default Drive      "
            f"{CONFIG['default_drive']}"
        )

        print(
            f"5  Status Bar         "
            f"{CONFIG['show_status']}"
        )

        print()
        print("Q  Back")

        choice = input(
            f"\n{C.BOLD}SETTINGS > {C.RESET}"
        ).strip().lower()

        if choice == "q":
            return

        if choice == "1":

            theme = input(
                "Theme name: "
            ).strip()

            if theme:
                CONFIG["theme"] = theme

            save_config(CONFIG)

        elif choice == "2":

            CONFIG["confirm_delete"] = (
                not CONFIG["confirm_delete"]
            )

            save_config(CONFIG)

        elif choice == "3":

            CONFIG["search_hidden"] = (
                not CONFIG["search_hidden"]
            )

            save_config(CONFIG)

        elif choice == "4":

            drive = input(
                "Default drive/folder: "
            ).strip()

            if drive and os.path.exists(drive):
                CONFIG["default_drive"] = drive
                save_config(CONFIG)

            else:
                error(
                    "That location does not exist."
                )

            time.sleep(0.7)

        elif choice == "5":

            CONFIG["show_status"] = (
                not CONFIG["show_status"]
            )

            save_config(CONFIG)


# ============================================================
# 15. HELP
# ============================================================

def help_menu():

    while True:

        title("COMMANDER HELP")

        print(
            "COMMANDER is a collection of utilities"
        )

        print(
            "for managing and inspecting your PC."
        )

        print()

        print(
            "1  WhereIs"
        )

        print(
            "   Search the entire PC for files."
        )

        print()

        print(
            "2  SpaceHog"
        )

        print(
            "   Find the largest files and folders."
        )

        print()

        print(
            "3  LockBox"
        )

        print(
            "   Store files in a local password-protected vault."
        )

        print()

        print(
            "4  WhatIsThis"
        )

        print(
            "   Inspect file information and metadata."
        )

        print()

        print(
            "5  Focus"
        )

        print(
            "   Run a productivity timer."
        )

        print()

        print(
            "6  Command Bar"
        )

        print(
            "   Quickly launch programs and commands."
        )

        print()

        print(
            "7  System Monitor"
        )

        print(
            "   Monitor CPU, RAM, disk and processes."
        )

        print()

        print(
            "8  QuickClean"
        )

        print(
            "   Clean selected temporary locations."
        )

        print()

        print(
            "9  File Manager"
        )

        print(
            "   Browse and manage your filesystem."
        )

        print()

        print(
            "10 Network"
        )

        print(
            "   Test connectivity and network information."
        )

        print()

        print(
            "11 Windows Tools"
        )

        print(
            "   Launch useful Windows utilities."
        )

        print()

        print(
            "12 Clipboard"
        )

        print(
            "   Manage clipboard history."
        )

        print()

        print(
            "13 Notes"
        )

        print(
            "   Keep simple local notes."
        )

        print()

        print(
            "14 Settings"
        )

        print(
            "   Configure COMMANDER."
        )

        print()

        pause()

        return


# ============================================================
# FILE OPERATIONS
# ============================================================

def open_path(path):

    try:

        path = os.path.abspath(
            os.path.expandvars(
                str(path)
            )
        )

        if os.name == "nt":

            os.startfile(path)

        elif sys.platform == "darwin":

            subprocess.Popen(
                ["open", path]
            )

        else:

            subprocess.Popen(
                ["xdg-open", path]
            )

    except Exception as e:
        error(
            f"Could not open: {e}"
        )


def delete_path(path):

    path = Path(path)

    print()

    print(
        C.YELLOW
        + "DELETE:"
        + C.RESET
    )

    print(path)

    if CONFIG.get(
        "confirm_delete",
        True
    ):

        confirm = input(
            "Type DELETE to confirm: "
        )

        if confirm != "DELETE":

            warning("Cancelled.")
            return

    try:

        if path.is_dir():

            shutil.rmtree(path)

        else:

            path.unlink()

        success(
            "Deleted successfully."
        )

    except Exception as e:

        error(
            f"Could not delete: {e}"
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        main_menu()

    except KeyboardInterrupt:

        print()
        print(
            C.YELLOW
            + "\nCOMMANDER interrupted."
            + C.RESET
        )

    except Exception as e:

        print()
        print(
            C.RED
            + "COMMANDER encountered an unexpected error:"
            + C.RESET
        )

        print(e)

        pause()