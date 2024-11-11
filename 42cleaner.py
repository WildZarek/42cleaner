#!/usr/bin/env python3

# Cleaner script for 42 students. It will remove all the trash files from our home directory.
# -----
# Author: WildZarek
# 42login: dsarmien

import argparse
import os
import psutil
import subprocess
from glob import glob
from time import sleep

# Uncomment the following lines to print disk usage or use 'df -h' command on a terminal:
# print(f"Total: {round(home.total / (2**30), 2)} GiB")
# print(f"Used: {round(home.used / (2**30), 2)} GiB")
# print(f"Free: {round(home.free / (2**30), 2)} GiB")
# print(f"Percentage: {round(home.percent)}%")

def set_color(txt: str, color_name: str) -> str:
    color_list = {
        "red": 91,
        "green": 92,
        "yellow": 93,
        "blue": 94,
        "purple": 95,
        "cyan": 96,
        "white": 97
    }
    return f"\033[{color_list[color_name]}m{txt}\033[{color_list["white"]}m"

def show_banner() -> None:
    if not args.silent:
        banner = """\033[93m
  ____ ___      __                     
 / / /|_  |____/ /__ ___ ____  ___ ____
/_  _/ __// __/ / -_) _ `/ _ \/ -_) __/
 /_//____/\__/_/\__/\_,_/_//_/\__/_/   
\033[91m                       by WildZarek  

\033[94m42cleaner\033[96m | Cleaner script for 42 students.\033[97m

>> If you liked this tool, give it a \033[93m'★ Star'\033[97m at the repository. Thanks!
>> \033[34mhttps://github.com/WildZarek/42cleaner\033[97m
>>
>> Run the script with -h or --help for more information.
"""
        os.system("clear")
        print(banner)

def show_menu():
    print("Please choose an option:\n")
    print(f"1.{set_color(' Create an scheduled task', 'blue')}")
    print(f"2.{set_color(' Remove an scheduled task', 'blue')}")
    print(f"3.{set_color(' Run the script now', 'blue')}")
    print(f"q.{set_color(' Quit', 'blue')}")

    choice = input("\nEnter your choice (1/2/3/q): ").strip().lower()

    return choice

def set_args():
    parser = argparse.ArgumentParser(description="Cleaner script for 42 students.")
    parser.add_argument("-s", "--silent", action="store_true", help="run the script in silent mode without prompts")
    parser.add_argument("-v", "--verbose", action="store_true", help="run the script in verbose mode with additional prompts")
    return parser.parse_args()

def exec_command(command: list) -> str:
    cmd = subprocess.run(command, stdout=subprocess.PIPE)
    return cmd.stdout.decode('utf-8').strip()

def show_space(usr: str) -> str:
    used_space = round(psutil.disk_usage(f"/home/{usr}/").percent)
    free_space = 100 - used_space
    return f"{set_color(f'{used_space}% used', 'red')} | {set_color(f'{free_space}% free', 'green')}"

def clean() -> None:
    usr = exec_command(["whoami"])

    # Check if cleanup is necessary
    if psutil.disk_usage(f"/home/{usr}/").percent <= 60:
        if not args.silent:
            print(f"\n[{set_color('!', 'yellow')}] Nothing to clean. Space: {show_space(usr)}")
            print(f"\n[{set_color('<', 'red')}] Exiting...")
        return

    # Check for 'rm' binary
    rm_bin = exec_command(["which", "rm"])
    if not rm_bin:
        if not args.silent:
            print(f"{set_color('Error', 'red')}: {set_color('rm binary not found.', 'cyan')}")
        return

    # Paths for trash files
    trash_paths = [
        f"/home/{usr}/.local/share/Trash/*",
        f"/home/{usr}/.zcompdump*",
        f"/home/{usr}/.cache/*",
        f"/home/{usr}/.config/Code/Cache/*",
        f"/home/{usr}/.config/Code/CachedData/*",
        f"/home/{usr}/francinette/temp/*",
    ]

    # Cleanup snap-related files
    packages = glob(f"/home/{usr}/snap/*")
    print(f"[{set_color('i', 'blue')}] Found {set_color(str(len(packages)), 'cyan')} snap packages.\n")
    snap_deleted_files_count = 0
    for pkg in packages:
        if pkg.endswith("firefox") or pkg.endswith("slack"):
            cache_files = glob(f"{pkg}/common/.cache/*")
            snap_deleted_files_count += len(cache_files)
            os.system(f"{rm_bin} -rf {pkg}/common/.cache/*")
        versions = [v for v in os.listdir(pkg) if v not in {"common", "current"}]
        if len(versions) > 1:
            if args.verbose and not args.silent:
                print(f"[{set_color('!', 'yellow')}] Found {set_color(str(len(versions)), 'red')} versions of {set_color(pkg.split('/')[-1], 'green')}")
                print(f"[{set_color('-', 'red')}] Removing old versions...")
            for v in sorted(versions)[:-1]:
                snap_deleted_files_count += sum(len(f) for _, _, f in os.walk(f"{pkg}/{v}"))
                os.system(f"{rm_bin} -rf {pkg}/{v}")

    # Count trash files
    trash_files_count = sum(len(glob(path)) for path in trash_paths)

    # Total files deleted
    total_deleted_files_count = snap_deleted_files_count + trash_files_count

    if total_deleted_files_count == 0:
        if not args.silent:
            print(f"[{set_color('i', 'blue')}] No trash files found.")
    else:
        if not args.silent:
            print(f"[{set_color('!', 'yellow')}] Cleaning trash files...")
        for path in trash_paths:
            os.system(f"{rm_bin} -rf {path}")
        if not args.silent:
            sleep(2)
            print(f"[{set_color('-', 'red')}] Deleted {set_color(str(total_deleted_files_count), 'yellow')} files.")
            print(f"[{set_color('i', 'blue')}] Disk usage after clean: {show_space(usr)}")

# WORKING HERE

def clear_snap(usr: str) -> int:
    files_deleted = 0
    packages = glob(f"/home/{usr}/snap/*")
    print(f"[{Blue('i')}] Found {Cyan(str(len(packages)))} snap packages.\n")
    for pkg in packages:
        # Firefox's cleaning subroutine
        if pkg.split('/')[-1] == "firefox":
            firefox_cache = glob(f"{pkg}/common/.cache/*")
            files_deleted += len(firefox_cache)
            os.system(f"rm -rf {pkg}/common/.cache/*")
        # Slack's cleaning subroutine
        if pkg.split('/')[-1] == "slack":
            slack_cache = glob(f"{pkg}/common/.cache/*")
            files_deleted += len(slack_cache)
            os.system(f"rm -rf {pkg}/common/.cache/*")
            slack_versions = os.listdir(pkg)
            slack_versions.remove("common")
            slack_versions.remove("current")
            slack_latest_cache = glob(f"{pkg}/{slack_versions[0]}/.config/Slack/Cache/Cache_Data/*")
            files_deleted += len(slack_latest_cache)
            os.system(f"rm -rf {pkg}/{slack_versions[0]}/.config/Slack/Cache/Cache_Data/*")
        versions = os.listdir(pkg)
        versions.remove("common")
        versions.remove("current")
        if len(versions) > 1:
            print(f"[{Yellow('!')}] Found {Red(str(len(versions)))} versions of {Green(pkg.split('/')[-1])}")
            print(f"[{Red('-')}] Removing old versions...")
            sleep(2)
            for v in versions:
                if v != max(versions):
                    files_deleted += sum([len(f) for r, d, f in os.walk(f"{pkg}/{v}/")])
                    os.system(f"rm -rf {pkg}/{v}")
    return files_deleted

def clean() -> None:
    usr = exec_command("whoami")
    if need_space(usr):
        rm_bin = check_command("rm")
        if not rm_bin:
            print(f"{Red('Error')}: {Cyan('rm')} binary not found.")
            return
        else:
            # Trash files
            files_trash = glob(f"/home/{usr}/.local/share/Trash/*")
            # Cache files
            files_zcompdump = glob(f"/home/{usr}/.zcompdump*")
            files_cache = glob(f"/home/{usr}/.cache/*")
            files_vscode_cache = glob(f"/home/{usr}/.config/Code/Cache/*")
            files_vscode_cached_data = glob(f"/home/{usr}/.config/Code/CachedData/*")
            # Francinette files
            files_francinette = glob(f"/home/{usr}/francinette/temp/*")
            # Snap packages (revisions)
            files_snap = clear_snap(usr)
            
            total_files = len(files_zcompdump) + len(files_cache) + len(files_vscode_cache) \
                          + len(files_vscode_cached_data) + len(files_trash) \
                          + len(files_francinette) + files_snap
            if total_files == 0:
                print(f"[{Blue('i')}] No trash files found.")
                return
            else:
                clear_files = files_zcompdump + files_cache + files_vscode_cache \
                            + files_vscode_cached_data + files_trash + files_francinette
                print(f"[{Yellow('!')}] Cleaning trash files...")
                for f in clear_files:
                    os.system(f"{rm_bin} -rf {f}")
                sleep(2)
                # The total files deleted is not accurate because some files (inside folders) are not counted.
                # But it's enough to show the user that the script is working. So, 1 folder = 1 file (in some cases).
                print(f"[{Red('-')}] Deleted {Yellow(str(total_files))} trash files.")
                print(f"[{Blue('i')}] Disk usage after clean: {show_space(usr)}\n")
    else:
        print(f"[{Blue('i')}] No need to clean. You have enough space: {show_space(usr)}\n")
        return

if __name__ == "__main__":
    args = set_args()
    show_banner()
    clean()