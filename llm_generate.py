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


from helpers import*

def generate_lms(promt: str, system_prompt: str, model, temperature: float, top_p: float):
    chat = lms.Chat()
    chat.add_system_prompt(system_prompt)
    chat.add_user_message(promt)

    result = model.respond(chat, config={
    "temperature": temperature,
    "top_p": top_p,
    })
    return result.content
    

def generate_llama(llm, prompt, system_prompt,max_tokens,temperature,top_p):
    full_prompt = f"[INST] {system_prompt}\n\n{prompt} [/INST]"
    output = llm(
        prompt=full_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=["</s>", "[/INST]"],
        echo=False,
    )
    llm.reset()
    return output['choices'][0]['text'].strip()
    
     