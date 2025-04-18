import os
import requests
import yaml

# 获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

_config = load_config()
_EMBEDDING_URL = _config["embedding"]["api_url"]
_EMBEDDING_MODEL = _config["embedding"]["model"]
_API_KEY = _config["embedding"]["api_key"]

def get_embedding(text: str):
    headers = {
        "Authorization": f"Bearer {_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": _EMBEDDING_MODEL,
        "input": text,
        "encoding_format": "float"
    }

    response = requests.post(_EMBEDDING_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Embedding API Error: {response.text}")

    return response.json()["data"][0]["embedding"]