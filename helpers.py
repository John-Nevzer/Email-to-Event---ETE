from llama_cpp import Llama
import sys
import caldav
from email.header import decode_header
from datetime import datetime
import configparser
import requests
import subprocess
import time
import os
import platform
import re
import math
import psutil
import socket
import lmstudio as lms


######################################################################################
# memory is counted in GB

def get_RAM_total():
    ram = psutil.virtual_memory()
    return ram.total / (1024**3)

def get_RAM_available():
    ram = psutil.virtual_memory()
    return ram.available / (1024**3)



def get_VRAM_total(): #warning - this function is ganerated by AI

    system = platform.system()

    # ------------------------
    # Windows
    # ------------------------
    if system == "Windows":
        try:
            # WMIC vrací VRAM v bytech
            out = subprocess.check_output(
                "wmic path win32_VideoController get AdapterRAM",
                shell=True
            )
            lines = out.decode().splitlines()
            # Najdeme první číslo větší než 0
            for line in lines:
                line = line.strip()
                if line.isdigit() and int(line) > 0:
                    return int(line) / (1024**3)
        except:
            return 0

    # ------------------------
    # Linux
    # ------------------------
    elif system == "Linux":
        # Nejprve zkus DRM sysfs
        drm_path = "/sys/class/drm/"
        try:
            cards = [d for d in os.listdir(drm_path) if d.startswith("card")]
            for card in cards:
                vram_file = os.path.join(drm_path, card, "device/mem_info_vram_total")
                if os.path.exists(vram_file):
                    with open(vram_file) as f:
                        return int(f.read().strip()) / (1024**3)
        except:
            pass

        # NVIDIA fallback přes nvidia-smi
        try:
            out = subprocess.check_output(
                ["nvidia-smi","--query-gpu=memory.total","--format=csv,noheader,nounits"]
            )
            vram_mb = int(out.decode().strip().split()[0])
            return vram_mb / 1024
        except:
            pass

        # AMD fallback přes rocm-smi
        try:
            out = subprocess.check_output(["rocm-smi","--showmeminfo","vram"])
            # nutné parsovat podle výstupu
            lines = out.decode().splitlines()
            for line in lines:
                if "VRAM Total" in line:
                    parts = line.split()
                    for p in parts:
                        if p.isdigit():
                            return int(p) / 1024
        except:
            pass

    # ------------------------
    # Pokud nelze zjistit
    # ------------------------
    return 0
######################################################################################

def set_max_tokens(emails, prompt, model_min_context):
    # longest_chars podle délky těla zprávy
    if not emails:
        return len(prompt) + 300  # fallback pokud seznam prázdný
    longest_email_body = max(emails, key=lambda e: len(e.body)).body
    longest_chars = len(longest_email_body)
    tokens= int(longest_chars / 2) + len(prompt) + 300
    if tokens <int(model_min_context):
        return model_min_context
    return tokens

def get_current_datetime_formatted():
    return datetime.now().strftime("%Y-%m-%dT%H:%M")

def port_check(api_url, api_port):
    host = api_url.replace("http://", "").replace("https://", "")
    port = int(api_port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  
        return s.connect_ex((host, port)) == 0

def set_max_GPU(model_path: str, max_tokens: int):
    vram = get_VRAM_total()
    value = ((os.path.getsize(model_path) / (1024**3))+(int(max_tokens)*0.002))/vram
    if value < 0.9 :
        return 50 
    else :
        return 50 #int(1/(value+0.2))*100

def printRAM():
    print(f"Instaled  RAM: { get_RAM_total() } GB\nAvailable RAM: { get_RAM_available() } GB")

def printVRAM():
    print(f"Total VRAM: { get_VRAM_total() } GB")


def date_comparer(date_str: str) -> bool:

    """
    False = date is older then curent time
    True = date is in the future
    """

    date_str = date_str.strip()
    # oprava např. 2025-03-00
    date_str = re.sub(r'-(\d{2})-00T', r'-\1-01T', date_str)
    # ISO T → mezera
    date_str = date_str.replace("T", " ")
    # pokud není čas
    if " " not in date_str and len(date_str) == 10:
        date_str += " 00:00"

    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y %H:%M",
        "%d/%m/%Y %H:%M",
    ]

    dt = None
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    if dt is None:
        return False

    return dt >= datetime.now()