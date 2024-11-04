# Cleaner script for 42 school. It will remove all the trash files from our home directory.
#
# Author: WildZarek
# 42login : dsarmien

import os
import psutil
import subprocess
from glob import glob
from time import sleep

def check_command(command: str) -> str:
    cmd = subprocess.run(['which', command], stdout=subprocess.PIPE)
    return cmd.stdout.decode('utf-8').strip()

def exec_command(command: str) -> str:
    cmd = subprocess.run([command], stdout=subprocess.PIPE)
    return cmd.stdout.decode('utf-8').strip()

def need_space(usr: str) -> bool:
    home = psutil.disk_usage(f"/home/{usr}/")
    # print(f"Total: {round(home.total / (2**30), 2)} GiB")
    # print(f"Used: {round(home.used / (2**30), 2)} GiB")
    # print(f"Free: {round(home.free / (2**30), 2)} GiB")
    # print(f"Percentage: {round(home.percent)}%")
    if round(home.percent) > 70:
        return True
    else:
        return False

def clean() -> None:
    usr = exec_command("whoami")
    if need_space(usr):
        rm_bin = check_command("rm")
        if not rm_bin:
            print("Error: 'rm' binary not found.")
            return
        else:
            # 42 Cache files
            files_zcompdump = glob(f"/home/{usr}/.zcompdump*")
            # Trash files
            files_trash = glob(f"/home/{usr}/.local/share/Trash/*")
            # Francinette files
            files_francinette = glob(f"/home/{usr}/francinette/temp/*/*")

            total_files = len(files_zcompdump) + len(files_trash) + len(files_francinette)
            if total_files == 0:
                print("[i] No trash files found.")
                return
            else:
                clear_files = files_zcompdump + files_trash + files_francinette
                print("[!] Cleaning trash files...")
                for f in clear_files:
                    os.system(f"{rm_bin} -rf {f}")
                sleep(2)
                print(f"[i] Deleted {total_files} trash files...")
    else:
        print("[i] No need to clean.")
        return

if __name__ == "__main__":
    os.system("clear")
    clean()