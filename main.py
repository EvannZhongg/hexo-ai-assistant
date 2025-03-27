from flask import Flask, request, jsonify, session, Response, stream_with_context
from flask_cors import CORS
from deepseek_chat import ask_deepseek_stream
from embedder import get_embedding
import json
import numpy as np

app = Flask(__name__)
app.secret_key = "supersecret"
CORS(app, supports_credentials=True)

with open("vector_store.json", "r", encoding="utf-8") as f:
    vector_store = json.load(f)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.route("/ask", methods=["POST"])
def ask():
    query = request.json.get("query")
    query_vec = get_embedding(query)

    results = sorted(
        vector_store,
        key=lambda x: cosine_similarity(query_vec, x["embedding"]),
        reverse=True
    )[:3]

    context = "\n\n".join([f"{r['title']}:\n{r['text']}" for r in results])
    context_prompt = f"以下是博客内容节选，请根据这些内容回答用户的问题：\n\n{context}"

    history = session.get("history", [])
    history.append({"role": "user", "content": query})

    messages = [
        {"role": "system", "content": "你是一个博客问答助手。请根据提供的内容回答用户问题。"},
        {"role": "user", "content": context_prompt}
    ] + history

    def generate():
        collected = ""
        for chunk in ask_deepseek_stream(messages):
            print(chunk, end="", flush=True)
            collected += chunk
            yield chunk

        # 📌 加入参考链接区块（前端也能收到）
        if results:
            ref_block = "\n\n> 📚 **参考内容来源：**\n"
            for r in results:
                ref_block += f"> - [{r['title']}]({r['url']})\n"

            yield ref_block
            collected += ref_block

        print("\n🧠 模型完整输出结束。\n")

        history.append({"role": "assistant", "content": collected})
        session["history"] = history[-10:]

    return Response(stream_with_context(generate()), content_type="text/plain")

@app.route("/reset", methods=["POST"])
def reset():
    session["history"] = []
    return jsonify({"status": "ok", "message": "会话已重置"})

if __name__ == "__main__":
    app.run(port=5000, threaded=True)
