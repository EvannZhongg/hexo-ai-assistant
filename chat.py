import yaml
from openai import OpenAI

def load_config():
    with open("config.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

_config = load_config()

# 通用 OpenAI 接口客户端
client = OpenAI(
    api_key=_config["chat"]["api_key"],
    base_url=_config["chat"]["api_url"]  # 可支持 https://api.openai.com/v1 或 DeepSeek 等兼容地址
)

def ask_stream(messages):
    response = client.chat.completions.create(
        model=_config["chat"]["model"],
        messages=messages,
        stream=True
    )

    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
