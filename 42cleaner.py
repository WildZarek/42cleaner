#!/usr/bin/env python3

# Cleaner script for 42 students. It will remove all the trash files from our home directory.
# --------------------
# Author: WildZarek
# 42login: dsarmien
# --------------------
# Collab: 4ndymcfly

import argparse
import os
import psutil
import re
import subprocess
from glob import glob
from time import sleep

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
    return f"\033[{color_list[color_name]}m{txt}\033[{color_list['white']}m"

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
>> \033[95mhttps://github.com/WildZarek/42cleaner\033[97m

(\033[94mRun the script with \033[97m-h\033[94m or \033[97m--help\033[94m for more information.\033[97m)
\033[92m------------------------------------------------------------------------\033[97m
"""
        os.system("clear")
        print(banner)

def show_menu():
    print("Please choose an option:\n")
    print(f"1.{set_color(' Create an scheduled task', 'yellow')}")
    print(f"2.{set_color(' Remove an scheduled task', 'yellow')}")
    print(f"3.{set_color(' Run the script now', 'yellow')}")
    print(f"q.{set_color(' Quit', 'yellow')}")

    choice = input("\nEnter your choice (1/2/3/q): ").strip().lower()

    return choice

def set_args():
    parser = argparse.ArgumentParser(description="Cleaner script for 42 students.")
    parser.add_argument("-s", "--silent", action="store_true", help="run the script in silent mode without prompts")
    parser.add_argument("-v", "--verbose", action="store_true", help="run the script in verbose mode with additional prompts")
    return parser.parse_args()

def exec_command(command: list) -> str:
    cmd = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
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
        versions = [v for v in os.listdir(pkg) if v not in {"common", "current"}]
        if pkg.endswith("firefox") or pkg.endswith("slack"):
            cache_files = glob(f"{pkg}/common/.cache/*")
            snap_deleted_files_count += len(cache_files)
            os.system(f"{rm_bin} -rf {pkg}/common/.cache/*")
            if pkg.endswith("slack"):
                slack_latest_cache = glob(f"{pkg}/{max(versions)}/.config/Slack/Cache/Cache_Data/*")
                snap_deleted_files_count += len(slack_latest_cache)
                os.system(f"{rm_bin} -rf {pkg}/{max(versions)}/.config/Slack/Cache/Cache_Data/*")
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
            if args.verbose:
                print(f"[{set_color('-', 'red')}] Deleted {set_color(str(total_deleted_files_count), 'yellow')} files.")
        print(f"[{set_color('i', 'blue')}] Disk usage after clean: {show_space(usr)}")

def schedule_task() -> None:
    if args.silent:
        return  # Skip task scheduling in silent mode

    choice = show_menu()

    script_path = os.path.abspath(__file__)
    cron_line = f"{script_path} --silent &> /dev/null"

    if choice == '1':
        current_cron = exec_command(["crontab", "-l"])
        if cron_line in current_cron:
            print(f"\n{set_color('Info', 'blue')}: A scheduled task already exists for this script.")
            return

        interval_options = {
            '1': "*/6 * * * *",
            '2': "*/8 * * * *",
            '3': "*/12 * * * *"
        }
        print("\nChoose an interval for the scheduled task:\n")
        print(f"1.{set_color(' Every 6 hours', 'blue')}")
        print(f"2.{set_color(' Every 8 hours', 'blue')}")
        print(f"3.{set_color(' Every 12 hours', 'blue')}")

        interval_choice = input("\nEnter your choice (1/2/3): ").strip()
        interval = interval_options.get(interval_choice)
        if not interval:
            print(f"\n{set_color('Error', 'red')}: Invalid choice.")
            return

        # Extract the number from the interval string
        interval_number = re.search(r'\d+', interval).group()

        full_cron_line = f"{interval} {cron_line}"
        os.system(f"(crontab -l; echo '{full_cron_line}') | crontab -")
        print(f"\n{set_color('Success', 'green')}: Scheduled task created to run every {set_color(interval_number, 'yellow')} hours.")
    elif choice == '2':
        current_cron = exec_command(["crontab", "-l"])
        if cron_line not in current_cron:
            print(f"\n{set_color('Info', 'blue')}: No scheduled task found for this script.")
        else:
            new_cron = "\n".join([line for line in current_cron.splitlines() if cron_line not in line])
            os.system(f"echo '{new_cron}' | crontab -")
            print(f"\n{set_color('Success', 'green')}: Scheduled task removed.")
    elif choice == '3':
        clean()
    elif choice == 'q':
        print(f"\n{set_color('Bye. Have a nice day!', 'green')}")

if __name__ == "__main__":
    args = set_args()
    show_banner()
    schedule_task()