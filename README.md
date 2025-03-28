# hexo-ai-assistant

---

### Hexo 博客智能问答助手 - 后端使用说明

> 本项目通过向量检索 + 大语言模型（RAG）结合本地 Hexo 博客内容，实现基于语义的智能问答接口。

---

## 项目结构

```
HexoAgent/
│
├── build_vector_store.py       # 向量库和标题映射构建脚本
├── main.py                     # Flask 主服务入口（/ask 问答接口）
├── embedder.py                 # 嵌入向量生成器（调用第三方 API）
├── chat.py                     # 通用 LLM 聊天模块（OpenAI / DeepSeek）
├── vector_store.json           # 本地语义向量数据库（自动生成）
├── title_mapping.json          # 博客标题与链接映射表（自动生成）
├── config.yml                  # 所有路径、模型、API Key 配置集中管理
└── .venv/                      # 虚拟环境（可选）
```

---

## 1. 安装依赖

建议使用虚拟环境：

```bash
# 创建环境
python -m venv .venv
# 激活环境（Windows）
.venv\Scripts\activate
# 安装依赖
pip install -r requirements.txt
```

---

## 2. 配置项修改（`config.yml`）

```yaml
paths:
  blog_post_dir: /your/path/to/hexo/source/_posts     # 修改为你的博客 Markdown 路径
  vector_store: vector_store.json                     # 向量库保存路径，建议使用绝对路径
  title_mapping: title_mapping.json                   # 博客标题映射表路径，建议使用绝对路径

blog:
  base_url: https://your-github-pages-url.github.io   # 修改为你的博客地址（不含末尾 /）

embedding:
  api_url: https://api.siliconflow.cn/v1/embeddings    # 嵌入模型 API 地址
  model: BAAI/bge-large-zh-v1.5                         # 使用的中文嵌入模型
  api_key: <YOUR_EMBEDDING_API_KEY>                    # 替换为你的嵌入模型 API Key
  max_characters: 5000                                 # 每篇文章最大截取字符数

chat:
  api_url: https://api.deepseek.com/v1                 # Chat 模型 API 地址（可替换为 OpenAI）
  model: deepseek-chat                                 # 使用的模型名称
  api_key: <YOUR_CHAT_API_KEY>                         # 替换为你的 LLM 接口 Key

server:
  port: 5000                                           # 后端服务运行端口（默认5000）

```

---

## 3. 构建向量库 & 标题映射表

```bash
python build_vector_store.py
```

生成文件：

- `vector_store.json`: 含每篇文章的文本和语义向量
- `title_mapping.json`: 含每篇文章的标题 + 主标题 + 链接

博客格式续遵循以下格式：
```
---
title: Article Title
date: YYYY-MM-DD HH:mm:ss
tags: [No impact]
categories: No impact
---
# Main Title

Text content.
```

---

## 4. 启动后端问答服务

```bash
python main.py
# 或使用自动 reload
flask run --port 5000
```

将启动本地服务：
```
http://127.0.0.1:5000/ask
```

---

使用 Ngrok 暴露本地服务：

```bash
ngrok http 5000
```

将 Ngrok 地址填入 `chatbot.ejs` 的链接中：

```
    const response = await fetch('https://***.ngrok-free.app/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ query })
    });
```

访问你的模型问答接口。

---

## 💡 常用命令速览

```bash
# 构建向量库
python build_vector_store.py

# 启动后端服务
python main.py

# 启动穿透（需安装 ngrok）
ngrok http 5000
```

---

即可实现完整博客问答体验。

---

如需将此说明导出为 `.md` 文档，我也可以直接帮你生成。是否要我输出为 `README.md` 文件并写入本地？
