#!/usr/bin/env python3

# Cleaner script for 42 students. It will remove all the trash files from our home directory.
# -----
# Author: WildZarek
# 42login: dsarmien

import os
import psutil
import subprocess
from glob import glob
from time import sleep

def Red(txt: str) -> None:
    return f"\033[91m{txt}\033[97m"

def Green(txt: str) -> None:
    return f"\033[92m{txt}\033[97m"

def Yellow(txt: str) -> None:
    return f"\033[93m{txt}\033[97m"

def Blue(txt: str) -> str:
    return f"\033[94m{txt}\033[97m"

def Purple(txt: str) -> str:
    return f"\033[95m{txt}\033[97m"

def Cyan(txt: str) -> str:
    return f"\033[96m{txt}\033[97m"

def White(txt: str) -> str:
    return f"\033[97m{txt}\033[97m"

def show_banner() -> None:
    banner = """\033[93m
  ____ ___      __                     
 / / /|_  |____/ /__ ___ ____  ___ ____
/_  _/ __// __/ / -_) _ `/ _ \/ -_) __/
 /_//____/\__/_/\__/\_,_/_//_/\__/_/   
\033[91m                       by WildZarek  

\033[94m42cleaner\033[96m | Cleaner script for 42 students.\033[97m

>> If you liked this tool, give it a \033[93m'★ Star'\033[97m at the repository. Thanks!
>> \033[34mhttps://github.com/WildZarek/42cleaner\033[97m
"""
    os.system("clear")
    print(banner)

def check_command(command: str) -> str:
    cmd = subprocess.run(['which', command], stdout=subprocess.PIPE)
    return cmd.stdout.decode('utf-8').strip()

def exec_command(command: str) -> str:
    cmd = subprocess.run([command], stdout=subprocess.PIPE)
    return cmd.stdout.decode('utf-8').strip()

def show_space(usr: str) -> str:
    home = psutil.disk_usage(f"/home/{usr}/")
    used_space = round(home.percent)
    free_space = 100 - used_space
    msg_space = f"{Red(str(used_space))}{Red('% used')} | {Green(str(free_space))}{Green('% free')}"
    return msg_space

def need_space(usr: str) -> bool:
    home = psutil.disk_usage(f"/home/{usr}/")
    # Uncomment the following lines to print disk usage or use 'df -h' command on a terminal:
    # print(f"Total: {round(home.total / (2**30), 2)} GiB")
    # print(f"Used: {round(home.used / (2**30), 2)} GiB")
    # print(f"Free: {round(home.free / (2**30), 2)} GiB")
    # print(f"Percentage: {round(home.percent)}%")
    if round(home.percent) > 60:
        return True
    else:
        return False

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
    show_banner()
    clean()