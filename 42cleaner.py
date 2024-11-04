# Cleaner script for 42 school. It will remove all the trash files from our home directory.
#
# Author: WildZarek
# 42login : dsarmien

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

def print_banner() -> None:
    banner = """\033[93m
  ____ ___      __                     
 / / /|_  |____/ /__ ___ ____  ___ ____
/_  _/ __// __/ / -_) _ `/ _ \/ -_) __/
 /_//____/\__/_/\__/\_,_/_//_/\__/_/   
\033[91m                       by WildZarek  

\033[94m42cleaner\033[96m | Cleaner script for 42 school.\033[97m

>> If you liked this tool, give it a \033[93m'★ Star'\033[97m at the repository. Thanks!
>> \033[34mhttps://github.com/WildZarek/42cleaner\033[97m
"""
    print(banner)

def check_command(command: str) -> str:
    cmd = subprocess.run(['which', command], stdout=subprocess.PIPE)
    return cmd.stdout.decode('utf-8').strip()

def exec_command(command: str) -> str:
    cmd = subprocess.run([command], stdout=subprocess.PIPE)
    return cmd.stdout.decode('utf-8').strip()

def need_space(usr: str) -> bool:
    home = psutil.disk_usage(f"/home/{usr}/")
    # Uncomment the following lines to print disk usage or use 'df -h' command on a terminal:
    # print(f"Total: {round(home.total / (2**30), 2)} GiB")
    # print(f"Used: {round(home.used / (2**30), 2)} GiB")
    # print(f"Free: {round(home.free / (2**30), 2)} GiB")
    # print(f"Percentage: {round(home.percent)}%")
    if round(home.percent) > 70:
        return True
    else:
        return False

def clear_snap(usr: str) -> int:
    files_deleted = 0
    packages = glob(f"/home/{usr}/snap/*")
    print(f"[{Blue('i')}] Found {len(packages)} snap packages.")
    for pkg in packages:
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
            # 42 Cache files
            files_zcompdump = glob(f"/home/{usr}/.zcompdump*")
            # Trash files
            files_trash = glob(f"/home/{usr}/.local/share/Trash/*")
            # Francinette files
            files_francinette = glob(f"/home/{usr}/francinette/temp/*")
            # Snap packages
            files_snap = clear_snap(usr)
            
            total_files = len(files_zcompdump) + len(files_trash) + len(files_francinette) + files_snap
            if total_files == 0:
                print(f"[{Blue('i')}] No trash files found.")
                return
            else:
                clear_files = files_zcompdump + files_trash + files_francinette
                print(f"[{Yellow('!')}] Cleaning trash files...")
                for f in clear_files:
                    os.system(f"{rm_bin} -rf {f}")
                sleep(2)
                print(f"[{Blue('i')}] Deleted {Green(str(total_files))} trash files...")
    else:
        home = psutil.disk_usage(f"/home/{usr}/")
        print(f"[{Blue('i')}] No need to clean. You have enough space ({Green(str(round(home.percent)))}{Green('% used')}).")
        return

if __name__ == "__main__":
    os.system("clear")
    print_banner()
    clean()