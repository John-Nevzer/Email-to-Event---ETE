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


from helpers import*


def prepare_lms(api_url: str, api_port: str, model_key, max_tokens, keepModelInMemory, offloadKVCacheToGpu):
    print("Spouštím LM Studio server...")
    subprocess.Popen(["lms", "server", "start", "--port", api_port])
    time.sleep(30)
    print(f"{api_url}:{api_port}")
    client = lms.Client(api_host=f"{api_url}:{api_port}")
    model = client.llm.model(
        model_key,
        config={
            "contextLength": max_tokens,
            "keepModelInMemory": keepModelInMemory,
            "offloadKVCacheToGpu": offloadKVCacheToGpu
        }
    )
    return client, model

"""Corresponding typed dictionary definition for LlmLoadModelConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    
    gpu: NotRequired[GpuSettingDict | None]
    gpuStrictVramCap: NotRequired[bool | None]
    offloadKVCacheToGpu: NotRequired[bool | None]
    contextLength: NotRequired[Annotated[int, Meta(ge=1)] | None]
    ropeFrequencyBase: NotRequired[float | None]
    ropeFrequencyScale: NotRequired[float | None]
    evalBatchSize: NotRequired[Annotated[int, Meta(ge=1)] | None]
    flashAttention: NotRequired[bool | None]
    keepModelInMemory: NotRequired[bool | None]
    seed: NotRequired[int | None]
    useFp16ForKVCache: NotRequired[bool | None]
    tryMmap: NotRequired[bool | None]
    numExperts: NotRequired[int | None]
    llamaKCacheQuantizationType: NotRequired
"""


def prepare_llama(
    model_path: str,
    max_tokens: int,
    gpu_layers: int,

    ):
    print("Načítám model přes llama.cpp...")    
    llm = Llama(
        model_path=model_path,
        n_ctx=max_tokens,
        n_threads=10,
        n_gpu_layers=gpu_layers,
        verbose=False
    )
    return llm

def unload_lms(client, model):
    model.unload()
    client.close()
    subprocess.run(["lms", "server", "stop"], check=False)
#/api/v1/models/unload

#is placed in main
"""
def unload_llama():
    llm=None
    gc.collect()
"""
