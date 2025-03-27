import os
import json
import markdown
import frontmatter
from embedder import get_embedding
from datetime import datetime
import sys
import io

# 设置标准输出的编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

POST_PATH = r"D:\Blog\source\_posts"  # 请根据你的实际路径调整
OUTPUT_PATH = "D:/Personal_Project/HexoAgent/vector_store.json"
BASE_URL = "https://evannzhongg.github.io"  # 改成你的博客地址

def build_vector_store():
    vector_store = []

    for filename in os.listdir(POST_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(POST_PATH, filename)

            # 使用 frontmatter.load 直接读取文件路径
            post = frontmatter.load(filepath)

            title = post.get("title", filename.replace(".md", ""))
            content = markdown.markdown(post.content)
            text = content.replace("<p>", "").replace("</p>", "").strip()
            date = post.get("date", datetime.now())

            # 解析日期
            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date)
                except Exception:
                    date = datetime.now()
            date_path = date.strftime("%Y/%m/%d")

            # 构建博客访问 URL
            url_title = title.replace(" ", "-").replace("/", "-")
            full_url = f"{BASE_URL}/{date_path}/{url_title}/"

            # 获取嵌入向量（截取前 1000 字符）
            embedding = get_embedding(text[:5000])
            vector_store.append({
                "title": title,
                "text": text[:5000],
                "path": filepath,
                "url": full_url,
                "embedding": embedding
            })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(vector_store, f, ensure_ascii=False, indent=2)

    # 修改这里的输出，避免使用可能引起问题的 Unicode 字符
    print(f"向量库已保存到 {OUTPUT_PATH}")

if __name__ == "__main__":
    build_vector_store()