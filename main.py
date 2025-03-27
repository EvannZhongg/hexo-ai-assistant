from flask import Flask, request, jsonify, session, Response, stream_with_context
from flask_cors import CORS
from deepseek_chat import ask_deepseek_stream
from embedder import get_embedding
import json
import numpy as np

app = Flask(__name__)
app.secret_key = "supersecret"
CORS(app, supports_credentials=True)

# 加载向量库
with open("vector_store.json", "r", encoding="utf-8") as f:
    vector_store = json.load(f)

# 加载博客标题映射表
with open("title_mapping.json", "r", encoding="utf-8") as f:
    title_mapping = json.load(f)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.route("/ask", methods=["POST"])
def ask():
    query = request.json.get("query")
    query_vec = get_embedding(query)

    # 语义匹配最近的内容
    results = sorted(
        vector_store,
        key=lambda x: cosine_similarity(query_vec, x["embedding"]),
        reverse=True
    )[:3]

    # 构建内容上下文
    context = "\n\n".join([f"{r['title']}:\n{r['text']}" for r in results])

    # 构建博客标题索引表（供模型参考）
    title_table = "\n".join(
        [f"- 标题：{item['title']} / 主标题：{item['main_heading']} / 链接：{item['permalink']}" for item in title_mapping]
    )

    context_prompt = (
        "以下是用户提问相关的博客内容节选。\n\n"
        "你可以结合下面的博客标题索引表来理解这些内容属于哪些具体博客，并在回答中引用标题，并附上链接（使用 markdown 链接格式）。\n\n"
        "如果回答中使用了某篇博客中的观点或结论，请在正文中使用链接进行引用。\n\n"
        f"【博客标题索引】:\n{title_table}\n\n"
        f"【语义相关内容】:\n{context}"
    )

    # 获取上下文历史
    history = session.get("history", [])
    history.append({"role": "user", "content": query})

    # 构建完整消息序列
    messages = [
        {"role": "system", "content": "你是一个 Hexo 博客智能问答助手，擅长结合博客内容给出精准、引用明确的解答。请在回答中引用使用到的博客标题，并附上链接。"},
        {"role": "user", "content": context_prompt}
    ] + history

    # 流式生成回答
    def generate():
        collected = ""
        for chunk in ask_deepseek_stream(messages):
            print(chunk, end="", flush=True)
            collected += chunk
            yield chunk

        print("\n模型完整输出结束。\n")
        history.append({"role": "assistant", "content": collected})
        session["history"] = history[-10:]

    return Response(stream_with_context(generate()), content_type="text/plain")

@app.route("/reset", methods=["POST"])
def reset():
    session["history"] = []
    return jsonify({"status": "ok", "message": "会话已重置"})

if __name__ == "__main__":
    app.run(port=5000, threaded=True)
