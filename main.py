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
import gc

from email_client import*
from calendar_client import add_event
from helpers import*
from llm_load import prepare_lms,prepare_llama, unload_lms
from llm_generate import generate_lms, generate_llama
########################################################################################################
########################################################################################################
#Set variables
#Loadable
# paths (relativní cesty)
main_path=  os.path.join(os.path.dirname(os.path.abspath(__file__)),"config")
lm_studio_run_path = r".\LM Studio.exe"#for navigation to .exe
lm_studio_cli_path = r".\resources\app\.webpack\lms.exe"#added in comand, not change
default_promt_path = os.path.join(main_path, "default.promt.ini")
custom_promt_path = os.path.join(main_path, "custom.promt.ini")
auto_response_path = os.path.join(main_path, "auto.response.ini")
config_path = os.path.join(main_path, "config.ini")
GUI_lang_path = os.path.join(main_path, "GLJl.lang.ini")

# lm settings
api_url = "127.0.0.1"
api_port= "1234"
api_url_tail="/v1/chat/completions"
model_key = "gemma-3-27b-it-qat"
max_tokens = 4000
gpu_layers = 20
keepModelInMemory = True
offloadKVCacheToGpu = True

client: vars
model: vars
llm: vars

#Constant
TIMEOUT = 3600

########################################################################################################
#set parse promt

print("Program started - start time")
print(get_current_datetime_formatted())
print("Resources")
printRAM()
printVRAM()

try:
    with open(default_promt_path, 'r', encoding='utf-8') as default_promt_file:
        default_promt = default_promt_file.read()
    with open(custom_promt_path, 'r', encoding='utf-8') as custom_promt_file:
        custom_promt = custom_promt_file.read()
except FileNotFoundError as e:
    print(f"Soubor nebyl nalezen: {e}")
    exit(1)

EVENT_EXTRACTION_PROMPT = (
    default_promt+
    "Today date: " + get_current_datetime_formatted() 
    +("\nOthers commands: " + custom_promt if custom_promt.strip() else "")
)

########################################################################################################
#load config.ini

config = configparser.ConfigParser()
config.read(config_path)
print("config path:")
print(config_path)
# načtení hodnot jako string, z .ini souboru
email_user = config["EMAIL"]["email_user"]
email_pass = config["EMAIL"]["email_pass"]
email_folder = config["EMAIL"]["email_folder"]
email_imap_server = config["EMAIL"]["email_imap_server"]
email_SSL_port= config["EMAIL"]["email_SSL_port"]

calendar_user = config["CALENDAR"]["calendar_user"]
calendar_pass = config["CALENDAR"]["calendar_pass"]
calendar_id = config["CALENDAR"]["calendar_id"]
calendar_icalendar_server = config["CALENDAR"]["calendar_icalendar_server"]

model_path = config["MODEL"]["model_path"]
use_lm_studio_api = config["MODEL"]["use_lm_studio_api"]
lm_studio_path = config["MODEL"]["lms_path"]

model_temperature = config.get("MODEL", "model_temperature", fallback="0.75")
model_topp = config.get("MODEL", "model_topp", fallback="0.9")
model_min_context = config.get("MODEL", "model_min_context", fallback="2500")
offloadKVCacheToGpu = config.getboolean("MODEL", "offloadKVCacheToGpu", fallback=False)
keepModelInMemory = config.getboolean("MODEL", "keepModelInMemory", fallback=True)
flash_attention = config.getboolean("MODEL", "flash_attention", fallback=False)


model_path = os.path.abspath(model_path)
print(f"konverze na absulutní: {model_path}")

if not os.path.isfile(model_path):
    print(f"CHYBA: Soubor modelu neexistuje: {model_path}")
    sys.exit(1)

lm_studio_path = os.path.join(lm_studio_path, lm_studio_run_path.lstrip(os.sep))  #absolutní cesty k .exe souborům
lm_studio_cli_path = os.path.join(lm_studio_path, lm_studio_cli_path.lstrip(os.sep))  # stejné pro cli cestu
print("Cesty k lm studio")
print(lm_studio_path, lm_studio_cli_path)

########################################################################################################
def unload_llama():
    global llm
    llm=None
    gc.collect()
########################################################################################################

#zpracovani #nacteni emailu
print("Reading emails")
emails= read_inbox(email_imap_server, email_SSL_port,email_user, email_pass,email_folder)
print(f"Zpracovávání: {len(emails)} emailů")#celkovy pocet objekt;
if len(emails)==0:
    print("No email found. Program ended.")
    sys.exit(1)
max_tokens=set_max_tokens(emails, EVENT_EXTRACTION_PROMPT, model_min_context)
gpu_layers = set_max_GPU(model_path, max_tokens)
print("Emails prepared and max context seted on")
print(max_tokens)

########################################################################################################

if use_lm_studio_api == '1':
    print("kontrola portů")    
    if not port_check(api_url, api_port):
        print("Port je volný")
    else:
        print(f"Port {api_port} je obsazený, LM Studio nelze spustit.")

    blob = prepare_lms(api_url, api_port, model_key, int(max_tokens), bool(keepModelInMemory), bool(offloadKVCacheToGpu))
    client = blob[0]
    model = blob[1]

else:
    llm = prepare_llama(model_path=model_path, gpu_layers=int (gpu_layers), max_tokens=int(max_tokens))
    print("Llama úspěšně připraveno.")


########################################################################################################

response_text: str= "NULL"
if use_lm_studio_api == '1':  # Lokální Llama.cpp
    i=0
    for input in emails:
        
        response_text = generate_lms(input.to_text_calendar(), EVENT_EXTRACTION_PROMPT, model, float( model_temperature), float (model_topp))
        response_lines = [line.strip() for line in response_text.split("\n") if line.strip()]
        emails[i].processed=True
        
        print(f"{len(response_lines)} událostí nalezeno")
        for res in response_lines:
            print(res)
            response = res.split(";")
            if len(response) == 3 and response[0] != "NULL":
                header, summary, date = response
                print(f"Event - header: {header}; summary: {summary}; date: {date}")
                add_event(header, summary, date, calendar_icalendar_server, calendar_user, calendar_pass,calendar_id)
    i=i+1
else:
    i=0
    for input in emails:
   
        response_line = generate_llama(llm,input, EVENT_EXTRACTION_PROMPT, int(max_tokens), float( model_temperature), float (model_topp)).split("\n")    
        emails[i].processed=True
        for res in response_line:
            print(res)
            response = res.split(";")
            if len(response) == 3 and response[0] != "NULL":
                print(response)
                print("Event - header: "+response[0]+"; sumary:"+response[1]+"; date: "+response[2])
                add_event(response[0],response[1],response[2],calendar_icalendar_server, calendar_user, calendar_pass,calendar_id)
    i=i+1
    print("LM Studio ukončeno.")


########################################################################################################


unload_llama()
unload_lms(client, model)
client.close()

print("Program ended - in time")
print(get_current_datetime_formatted())
print("Resources")
printRAM()
printVRAM()
print("Tasks ended. Sources is free.")
sys.exit(1)