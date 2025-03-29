# hexo-ai-assistant

This project combines vector retrieval and large language models (RAG) to create a semantic-based intelligent Q&A interface for your local Hexo blog.

![image](https://github.com/user-attachments/assets/40f5a3c5-74a6-453b-b83b-6152c5b40990)

---

## Project Structure

```
📁 D:/YourProjects/
├── 📁 Blog/                              # Hexo blog project directory (initialized via `hexo init`)
│   ├── source/_posts/                   # Markdown blog post files
│   ├── themes/hexo-theme-xxx/           # Custom Hexo theme
│   │   ├── layout/_partial/
│   │   │   ├── footer.ejs               # Inject chatbot here via partial
│   │   │   ├── chatbot.ejs              # Chatbot UI template (included in footer)
│   │   │   └── ...
│   │   └── ...  
│   ├── scripts/auto_vector.js           # Auto vector builder (executed via Hexo lifecycle)
│   └── ...                              # Other Hexo configuration files
│
├── 📁 hexo-ai-assistant/                # AI Q&A backend project (retrieval-augmented generation)
│   ├── build_vector_store.py            # Script to build semantic vector DB and title mapping
│   ├── main.py                          # Flask server entry point exposing `/ask` endpoint
│   ├── embedder.py                      # Embedding generator (calls external API)
│   ├── chat.py                          # Unified LLM API client (OpenAI / DeepSeek compatible)
│   ├── vector_store.json                # Semantic vector store (auto-generated)
│   ├── title_mapping.json               # Blog title ↔ permalink mapping table (auto-generated)
│   ├── config.yml                       # Centralized config for paths, API keys, and models
│   └── .venv/                           # Python virtual environment (optional)

```

---

## Execution Principle (Project Workflow)

1. **Semantic Knowledge Construction Stage** (executed by `build_vector_store.py`):
   - Scans blog Markdown source files and extracts article content.
   - Generates semantic vectors using embedding models (e.g., BGE).
   - Builds `vector_store.json` and `title_mapping.json` for later use in Q&A.

2. **User Q&A Handling Stage** (provided by `main.py` API):
   - Users send questions via the frontend.
   - The backend converts the query to an embedding and finds related articles.
   - Constructs a prompt with semantic content and a title index, and sends it to the language model.
   - The model returns an answer with reference links, streamed to the frontend.

3. **Frontend Q&A Display Stage** (handled by `chatbot.ejs`):
   - Loads a chat interface that supports Markdown rendering and multi-turn conversation.
   - Requests are forwarded to the local backend or a public proxy address.

---

## 1. Install Dependencies

It is recommended to use a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Modify Configuration (`config.yml`)

```yaml
paths:
  blog_post_dir: /your/path/to/hexo/source/_posts     # Change to your blog Markdown path
  vector_store: vector_store.json                     # Vector store output path, use absolute if preferred
  title_mapping: title_mapping.json                   # Title mapping output path, use absolute if preferred

blog:
  base_url: https://your-github-pages-url.github.io   # Change to your blog base URL (no trailing slash)

embedding:
  api_url: https://api.siliconflow.cn/v1/embeddings    # Embedding model API
  model: BAAI/bge-large-zh-v1.5                         # Embedding model name
  api_key: <YOUR_EMBEDDING_API_KEY>                    # Replace with your embedding API key
  max_characters: 5000                                 # Maximum characters per article to embed

chat:
  api_url: https://api.deepseek.com/v1                 # Chat model API endpoint (can be OpenAI compatible)
  model: deepseek-chat                                 # Chat model name
  api_key: <YOUR_CHAT_API_KEY>                         # Replace with your LLM API key

server:
  port: 5000                                           # Local server port (default 5000)
```

---

## 3. Build Vector Store & Title Mapping

```bash
python build_vector_store.py
```

Generated files:

- `vector_store.json`: Contains each article's text and semantic embedding
- `title_mapping.json`: Contains title, main heading, and permalink for each article

Markdown format requirements:

```
---
title: Article Title
date: YYYY-MM-DD HH:mm:ss
tags: [...]  # No impact
categories: ...  # No impact
---
# Main Title  # Must be a first level title

Content...
```

---

## 4. Start the Backend Q&A Service

```bash
python main.py
```

After startup, the local API will be available at:

```
http://127.0.0.1:5000/ask
```

You can open `chat.html` in the browser to test and check if the answers are returned properly.

---

## 5. Configure Hexo Script

If everything above works correctly, integrate vector building into the Hexo generation flow.

### 1. Create Script File `scripts/auto_vector.js`:

```js
const { exec } = require("child_process");

hexo.extend.filter.register("before_generate", function () {
  console.log("Building blog vector store...");
  return new Promise((resolve, reject) => {
    exec("D:/your_project/.venv/Scripts/python build_vector_store.py", {
      cwd: "D:/your_project"
    }, (err, stdout, stderr) => {
      if (err) {
        console.error("Build failed:", stderr);
        reject(err);
      } else {
        console.log("Build succeeded");
        resolve();
      }
    });
  });
});
```

This script ensures the vector store is rebuilt automatically whenever `hexo g` is executed.

### 2. Include `chatbot.ejs` in Page Footer

Open the following file:

```
themes/hexo-theme-Chic/layout/_partial/footer.ejs
```

Add after the `</footer>` tag:

```html
<%- partial('chatbot') %>
```

Create a new file `chatbot.ejs` in:

```
themes/hexo-theme-Chic/layout/_partial/chatbot.ejs
```

Paste the contents of `chatbot.ejs` (see the project repo for full code).

Rebuild and preview your Hexo site:

```bash
hexo clean
hexo g
hexo d
```

The result should be similar to:

```
[screenshot image here]
```

---

## 6. Expose Local Backend via Ngrok (Optional)

After confirming local success, use Ngrok to expose your service:

```bash
ngrok http 5000
```

Copy the address `https://xxx.ngrok-free.app/ask` into your frontend `chatbot.ejs`:

```js
const response = await fetch("https://xxx.ngrok-free.app/ask", {...});
```

Note: Using Ngrok for production is not secure. You should consider using a proxy or deploy your backend to a public server.

---

## Full Workflow Summary

1. Write blog posts in Markdown format (ensuring required metadata and main heading).
2. Run `build_vector_store.py` to extract and embed blog content.
3. Launch `main.py` to start the local Q&A API.
4. Use the chat frontend to ask questions; requests are routed via Ngrok if needed.
5. The model responds using retrieved content, with proper references and permalinks.

