import os
from openai import OpenAI
from dotenv import load_dotenv

# 载入 .env 中的 API 密钥
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 初始化 DeepSeek API 客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def ask_deepseek_stream(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.5,
        stream=True
    )
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta:
            yield chunk.choices[0].delta.content or ""

