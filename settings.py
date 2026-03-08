
import tkinter as tk
from tkinter import messagebox
import configparser
import platform
import subprocess
import os
import shutil
from datetime import datetime
import locale

#-------------------------------------------------------------------------------------------------------
languages = ["en", "cs", "ru", "fr", "de", "es"]

# Základní nastavení
title_text = "Settings"
email_user_text = "Email username"
email_pass_text = "Email password"
email_folder_text = "Email folder"
email_imap_server_text = "IMAP server"
email_SSL_port_text = "SSL port of IMAP server"
calendar_user_text = "Calendar username"
calendar_pass_text = "Calendar password"
calendar_id_text = "Calendar ID"
calendar_icalendar_server_text = "CalDAV server"

# Cesty k modelům
model_path_text = "LLM model path"
lms_path_text = "LM studio.exe path"

# Parametry modelu
model_temperature_text = "Model temperature"
model_topp_text = "Model top-p"
model_min_context_text = "Model minimum context length"
offloadKVCacheToGpu_text = "Offload KV cache to GPU"
keepModelInMemory_text = "Keep model in memory"
flash_attention_text = "Flash attention"

# Další nastavení
time_in_text = "Time in (HH:MM)"
save_config_text = "Save"
plan_script_text = "Plan"
use_lm_studio_api_text = "Use LM Studio API"

GUI_LANG = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config"), "gui.lang.ini")
CONFIG_FILE = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config"), "config.ini")

#-------------------------------------------------------------------------------------------------------
def detect_language():
    system_language = locale.getdefaultlocale()[0][:2]
    return languages.index(system_language) if system_language in languages else 0

#-------------------------------------------------------------------------------------------------------
def refresh_gui():
    bold_labels = [
        ((0, 0), email_user_text),
        ((1, 0), email_pass_text),
        ((2, 0), email_folder_text),
        ((3, 0), email_imap_server_text),
        ((4, 0), email_SSL_port_text),
        ((5, 0), calendar_user_text),
        ((6, 0), calendar_pass_text),
        ((7, 0), calendar_id_text),
        ((8, 0), calendar_icalendar_server_text),
        ((9, 0), model_path_text),
        ((10, 0), time_in_text),
        ((12, 0), lms_path_text),
        ((13, 0), model_temperature_text),
        ((14, 0), model_topp_text),
        ((15, 0), model_min_context_text),
        ((16, 0), offloadKVCacheToGpu_text),
        ((17, 0), keepModelInMemory_text),
        ((18, 0), flash_attention_text)
    ]
    for (row, col), text in bold_labels:
        for widget in root.grid_slaves(row=row, column=col):
            if isinstance(widget, tk.Label):
                widget.config(text=text)
                break

    # Aktualizace checkboxu
    for widget in root.grid_slaves(row=10, column=0):
        if isinstance(widget, tk.Checkbutton):
            widget.config(text=use_lm_studio_api_text)

    # Aktualizace tlačítek
    for widget in root.grid_slaves(row=12, column=0):
        if isinstance(widget, tk.Button):
            widget.config(text=save_config_text)
    for widget in root.grid_slaves(row=13, column=0):
        if isinstance(widget, tk.Button):
            widget.config(text=plan_script_text)

    root.title(title_text)

#-------------------------------------------------------------------------------------------------------
def change_language_wrapper(selection):
    index = languages.index(selection)
    change_language(index)
    refresh_gui()

#-------------------------------------------------------------------------------------------------------
def change_language(index):
    global title_text, email_user_text, email_pass_text, email_folder_text, email_imap_server_text, email_SSL_port_text
    global calendar_user_text, calendar_pass_text, calendar_id_text, calendar_icalendar_server_text
    global model_path_text, lms_path_text, model_temperature_text, model_topp_text, model_min_context_text
    global offloadKVCacheToGpu_text, keepModelInMemory_text, flash_attention_text
    global time_in_text, save_config_text, plan_script_text, use_lm_studio_api_text

    config = configparser.ConfigParser()
    config.read(GUI_LANG, encoding="utf-8")
    lang = languages[index]
    
    if config.has_section(lang):
        # Základní nastavení
        title_text = config.get(lang, 'title_text', fallback=title_text)
        email_user_text = config.get(lang, 'email_user_text', fallback=email_user_text)
        email_pass_text = config.get(lang, 'email_pass_text', fallback=email_pass_text)
        email_folder_text = config.get(lang, 'email_folder_text', fallback=email_folder_text)
        email_imap_server_text = config.get(lang, 'email_imap_server_text', fallback=email_imap_server_text)
        email_SSL_port_text = config.get(lang, 'email_SSL_port_text', fallback=email_SSL_port_text)
        calendar_user_text = config.get(lang, 'calendar_user_text', fallback=calendar_user_text)
        calendar_pass_text = config.get(lang, 'calendar_pass_text', fallback=calendar_pass_text)
        calendar_id_text = config.get(lang, 'calendar_id_text', fallback=calendar_id_text)
        calendar_icalendar_server_text = config.get(lang, 'calendar_icalendar_server_text', fallback=calendar_icalendar_server_text)

        # Cesty k modelům
        model_path_text = config.get(lang, 'model_path_text', fallback=model_path_text)
        lms_path_text = config.get(lang, 'lms_path_text', fallback=lms_path_text)
        use_lm_studio_api_text = config.get(lang, 'use_lm_studio_api_text', fallback=use_lm_studio_api_text)

        # Parametry modelu
        model_temperature_text = config.get(lang, 'model_temperature_text', fallback=model_temperature_text)
        model_topp_text = config.get(lang, 'model_topp_text', fallback=model_topp_text)
        model_min_context_text = config.get(lang, 'model_min_context_text', fallback=model_min_context_text)
        offloadKVCacheToGpu_text = config.get(lang, 'offloadKVCacheToGpu_text', fallback=offloadKVCacheToGpu_text)
        keepModelInMemory_text = config.get(lang, 'keepModelInMemory_text', fallback=keepModelInMemory_text)
        flash_attention_text = config.get(lang, 'flash_attention_text', fallback=flash_attention_text)

        # Čas a další ovládací prvky
        time_in_text = config.get(lang, 'time_in_text', fallback=time_in_text)
        save_config_text = config.get(lang, 'save_config_text', fallback=save_config_text)
        plan_script_text = config.get(lang, 'plan_script_text', fallback=plan_script_text)

#-------------------------------------------------------------------------------------------------------
change_language(detect_language())

#-------------------------------------------------------------------------------------------------------
# Načtení konfigurace
config = configparser.ConfigParser()
config.read(CONFIG_FILE, encoding="utf-8")

# E-mail
email_user_val = config.get("EMAIL", "email_user", fallback="")
email_pass_val = config.get("EMAIL", "email_pass", fallback="")
email_folder_val = config.get("EMAIL", "email_folder", fallback="")
email_imap_server_val = config.get("EMAIL", "email_imap_server", fallback="")
email_SSL_port_val = config.get("EMAIL", "email_SSL_port", fallback="")

# Kalendář
calendar_user_val = config.get("CALENDAR", "calendar_user", fallback="")
calendar_pass_val = config.get("CALENDAR", "calendar_pass", fallback="")
calendar_id_val = config.get("CALENDAR", "calendar_id", fallback="")
calendar_icalendar_server_val = config.get("CALENDAR", "calendar_icalendar_server", fallback="")

# Cesty k modelům
model_path_val = config.get("MODEL", "model_path", fallback="")
lms_path_val = config.get("MODEL", "lms_path", fallback="")  # opravena chyba v názvu
use_lm_studio_api_val = config.getboolean("MODEL", "use_lm_studio_api", fallback=False)

# Parametry modelu
model_temperature_val = config.get("MODEL", "model_temperature", fallback="1.0")
model_topp_val = config.get("MODEL", "model_topp", fallback="0.9")
model_min_context_val = config.get("MODEL", "model_min_context", fallback="512")
offloadKVCacheToGpu_val = config.getboolean("MODEL", "offloadKVCacheToGpu", fallback=False)
keepModelInMemory_val = config.getboolean("MODEL", "keepModelInMemory", fallback=True)
flash_attention_val = config.getboolean("MODEL", "flash_attention", fallback=True)

# Čas / plán
time_val = config.get("SCHEDULE", "time", fallback="00:00")
default_hour, default_minute = time_val.split(":") if ":" in time_val else ("00", "00")

#-------------------------------------------------------------------------------------------------------
def save_config():
    cfg = configparser.ConfigParser()
    cfg["EMAIL"] = {
        "email_user": email_user.get(),
        "email_pass": email_pass.get(),
        "email_folder": email_folder.get(),
        "email_imap_server": email_imap_server.get(),
        "email_SSL_port": email_SSL_port.get()
    }
    cfg["CALENDAR"] = {
        "calendar_user": calendar_user.get(),
        "calendar_pass": calendar_pass.get(),
        "calendar_id": calendar_id.get(),
        "calendar_icalendar_server": calendar_icalendar_server.get()
    }
    cfg["MODEL"] = {
    "model_path": model_path.get(),
    "use_lm_studio_api": str(use_lm_studio_api.get()),  # Ukládáme jako "True"/"False"
    "lms_path": lms_path.get(),  # opraveno z lms_path_val

    # Parametry modelu
    "model_temperature": model_temperature.get(),
    "model_topp": model_topp.get(),
    "model_min_context": model_min_context.get(),
    "offloadKVCacheToGpu": str(offloadKVCacheToGpu.get()),  # Boolean jako string
    "keepModelInMemory": str(keepModelInMemory.get()),      # Boolean jako string
    "flash_attention": str(flash_attention.get())          # Boolean jako string
    }
    cfg["SCHEDULE"] = {
        "time": f"{hour.get()}:{minute.get()}"
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)
    messagebox.showinfo("Hotovo", "Konfigurace uložena.")

#-------------------------------------------------------------------------------------------------------
def create_task_windows(base_dir, script_path, hh, mm):
    time_str = f"{hh:02}:{mm:02}"
    bat_path = os.path.join(base_dir, "run_ETE.bat")
    venv_python = os.path.join(base_dir, "venv", "Scripts", "python.exe")

    # Kontrola, zda cesty existují
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Adresář {base_dir} neexistuje.")
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Soubor {script_path} neexistuje.")

    with open(bat_path, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write(f'cd /d "{base_dir}"\n')
        f.write(f'call "{os.path.join(base_dir, "venv", "Scripts", "activate.bat")}"\n')
        f.write(f'"{venv_python}" "{script_path}" >> "{os.path.join(base_dir, "log.txt")}" 2>&1\n')

    try:
        subprocess.run([
            "schtasks", "/Create", "/SC", "DAILY",
            "/TN", "EmailToEvent-python_skript",
            "/TR", bat_path,  # bez uvozovek, subprocess.run je escapuje
            "/ST", time_str,
            "/F", "/RL", "LIMITED", "/RU", os.environ.get("USERNAME", os.getlogin()),
        ], check=True)
        print(f"Úloha naplánována na {time_str}.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při plánování: {e}")
        raise

def create_task_linux(base_dir, script_path, hh, mm):
    cron_line = f"{int(mm)} {int(hh)} * * * python3 {script_path}\n"
    subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -', shell=True)

def schedule_task():
    hh = hour.get()
    mm = minute.get()
    system = platform.system()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "main.py")
    if system == "Linux":
        create_task_linux(base_dir, script_path, hh, mm)
    elif system == "Windows":
        create_task_windows(base_dir, script_path, hh, mm)
    else:
        messagebox.showwarning("Nepodporováno", f"Plánování není podporováno na {system}.")
    messagebox.showinfo(plan_script_text + " OK")

#-------------------------------------------------------------------------------------------------------
# GUI
root = tk.Tk()
root.title(title_text)
root.geometry("900x750")  # Zvětšeno kvůli novému řádku
entry_width = 50
lang_var = tk.StringVar(root)
lang_var.set(languages[detect_language()])

# Email
tk.Label(root, text=email_user_text, anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(user@example.com)", anchor="w", font=("Arial", 8, "italic")).grid(row=0, column=1, sticky="w", padx=10, pady=0)
email_user = tk.Entry(root, width=entry_width); email_user.insert(0, email_user_val); email_user.grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text=email_pass_text, anchor="w", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(passWord123)", anchor="w", font=("Arial", 8, "italic")).grid(row=1, column=1, sticky="w", padx=10, pady=0)
email_pass = tk.Entry(root, show="*", width=entry_width); email_pass.insert(0, email_pass_val); email_pass.grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text=email_folder_text, anchor="w", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(MyFolderForETE)", anchor="w", font=("Arial", 8, "italic")).grid(row=2, column=1, sticky="w", padx=10, pady=0)
email_folder = tk.Entry(root, width=entry_width); email_folder.insert(0, email_folder_val); email_folder.grid(row=2, column=2, padx=10, pady=5)

# IMAP server → řádek 3
tk.Label(root, text=email_imap_server_text, anchor="w", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(imap.example.com)", anchor="w", font=("Arial", 8, "italic")).grid(row=3, column=1, sticky="w", padx=10, pady=0)
email_imap_server = tk.Entry(root, width=entry_width); email_imap_server.insert(0, email_imap_server_val); email_imap_server.grid(row=3, column=2, padx=10, pady=5)

# SSL port → řádek 4 (posunuto!)
tk.Label(root, text=email_SSL_port_text, anchor="w", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(usually 993)", anchor="w", font=("Arial", 8, "italic")).grid(row=4, column=1, sticky="w", padx=10, pady=0)
email_SSL_port = tk.Entry(root, width=entry_width); email_SSL_port.insert(0, email_SSL_port_val); email_SSL_port.grid(row=4, column=2, padx=10, pady=5)

# Calendar (posunuto o 1 řádek níže)
tk.Label(root, text=calendar_user_text, anchor="w", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(username)", anchor="w", font=("Arial", 8, "italic")).grid(row=5, column=1, sticky="w", padx=10, pady=0)
calendar_user = tk.Entry(root, width=entry_width); calendar_user.insert(0, calendar_user_val); calendar_user.grid(row=5, column=2, padx=10, pady=5)

tk.Label(root, text=calendar_pass_text, anchor="w", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(passWord456)", anchor="w", font=("Arial", 8, "italic")).grid(row=6, column=1, sticky="w", padx=10, pady=0)
calendar_pass = tk.Entry(root, show="*", width=entry_width); calendar_pass.insert(0, calendar_pass_val); calendar_pass.grid(row=6, column=2, padx=10, pady=5)

tk.Label(root, text=calendar_id_text, anchor="w", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(zhdfzkl4dbh4f7s4)", anchor="w", font=("Arial", 8, "italic")).grid(row=7, column=1, sticky="w", padx=10, pady=0)
calendar_id = tk.Entry(root, width=entry_width); calendar_id.insert(0, calendar_id_val); calendar_id.grid(row=7, column=2, padx=10, pady=5)

tk.Label(root, text=calendar_icalendar_server_text, anchor="w", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(https://caldav.example.com)", anchor="w", font=("Arial", 8, "italic")).grid(row=8, column=1, sticky="w", padx=10, pady=0)
calendar_icalendar_server = tk.Entry(root, width=entry_width); calendar_icalendar_server.insert(0, calendar_icalendar_server_val); calendar_icalendar_server.grid(row=8, column=2, padx=10, pady=5)

tk.Label(root, text=model_path_text, anchor="w", font=("Arial", 10, "bold")).grid(row=9, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="ETE(D:\models\llama_LLM.gguf)", anchor="w", font=("Arial", 8, "italic")).grid(row=9, column=1, sticky="w", padx=10, pady=0)
model_path = tk.Entry(root, width=entry_width); model_path.insert(0, model_path_val); model_path.grid(row=9, column=2, padx=10, pady=5)

tk.Label(root, text=time_in_text, anchor="w", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(17 35)", anchor="w", font=("Arial", 8, "italic")).grid(row=10, column=1, sticky="w", padx=10, pady=0)
hour = tk.Entry(root, width=5); hour.insert(0, default_hour); hour.grid(row=10, column=2, sticky="w", padx=(10,0), pady=5)
minute = tk.Entry(root, width=5); minute.insert(0, default_minute); minute.grid(row=10, column=2, sticky="e", padx=(0,10), pady=5)

use_lm_studio_api = tk.IntVar(value=1 if use_lm_studio_api_val else 0)
tk.Checkbutton(root, text=use_lm_studio_api_text, variable=use_lm_studio_api).grid(row=11, column=0, columnspan=2, sticky="w", padx=10, pady=8)

tk.Label(root, text=lms_path_text, anchor="w", font=("Arial", 10, "bold")).grid(row=12, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="(D:\programs\LM studio)", anchor="w", font=("Arial", 8, "italic")).grid(row=12, column=1, sticky="w", padx=10, pady=0)
lms_path = tk.Entry(root, width=entry_width); lms_path.insert(0, lms_path_val); lms_path.grid(row=12, column=2, padx=10, pady=5)

tk.Label(root, text=model_temperature_text, anchor="w", font=("Arial", 10, "bold")).grid(row=13, column=0, sticky="w", padx=10, pady=5)
model_temperature = tk.Entry(root, width=entry_width)
model_temperature.insert(0, model_temperature_val)
model_temperature.grid(row=13, column=2, padx=10, pady=5)

tk.Label(root, text=model_topp_text, anchor="w", font=("Arial", 10, "bold")).grid(row=14, column=0, sticky="w", padx=10, pady=5)
model_topp = tk.Entry(root, width=entry_width)
model_topp.insert(0, model_topp_val)
model_topp.grid(row=14, column=2, padx=10, pady=5)

tk.Label(root, text=model_min_context_text, anchor="w", font=("Arial", 10, "bold")).grid(row=15, column=0, sticky="w", padx=10, pady=5)
model_min_context = tk.Entry(root, width=entry_width)
model_min_context.insert(0, model_min_context_val)
model_min_context.grid(row=15, column=2, padx=10, pady=5)

tk.Label(root, text=offloadKVCacheToGpu_text, anchor="w", font=("Arial", 10, "bold")).grid(row=16, column=0, sticky="w", padx=10, pady=5)
offloadKVCacheToGpu = tk.IntVar(value=1 if offloadKVCacheToGpu_val else 0)
tk.Checkbutton(root, variable=offloadKVCacheToGpu).grid(row=16, column=2, sticky="w", padx=10, pady=5)

tk.Label(root, text=keepModelInMemory_text, anchor="w", font=("Arial", 10, "bold")).grid(row=17, column=0, sticky="w", padx=10, pady=5)
keepModelInMemory = tk.IntVar(value=1 if keepModelInMemory_val else 0)
tk.Checkbutton(root, variable=keepModelInMemory).grid(row=17, column=2, sticky="w", padx=10, pady=5)

tk.Label(root, text=flash_attention_text, anchor="w", font=("Arial", 10, "bold")).grid(row=18, column=0, sticky="w", padx=10, pady=5)
flash_attention = tk.IntVar(value=1 if flash_attention_val else 0)
tk.Checkbutton(root, variable=flash_attention).grid(row=18, column=2, sticky="w", padx=10, pady=5)

tk.Button(root, text=save_config_text, command=save_config, width=30, bg="green", fg="white").grid(row=19, column=0, columnspan=2, pady=10)
tk.Button(root, text=plan_script_text, command=schedule_task, width=30, bg="blue", fg="white").grid(row=20, column=0, columnspan=2, pady=10)

tk.Label(root, text="^", font=("Webdings", 20)).grid(row=19, column=2, sticky="e", padx=10, pady=5)
language_menu = tk.OptionMenu(root, lang_var, *languages, command=change_language_wrapper)
language_menu.grid(row=20, column=2, pady=10, padx=10, sticky="e")


#-------------------------------------------------------------------------------------------------------
root.mainloop()
