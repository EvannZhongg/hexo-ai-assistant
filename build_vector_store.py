import os
import json
import markdown
import frontmatter
from embedder import get_embedding
from datetime import datetime
import sys
import io
import re

# 设置 stdout 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

POST_PATH = r"D:\Blog\source\_posts"
VECTOR_STORE_PATH = "D:/Personal_Project/HexoAgent/vector_store.json"
MAPPING_PATH = "D:/Personal_Project/HexoAgent/title_mapping.json"
BASE_URL = "https://evannzhongg.github.io"

def extract_main_heading(md_text):
    match = re.search(r"^# (.+)$", md_text, re.MULTILINE)
    return match.group(1).strip() if match else ""

def build_vector_store():
    vector_store = []
    mapping_table = []

    for filename in os.listdir(POST_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(POST_PATH, filename)
            post = frontmatter.load(filepath)

            title = post.get("title", filename.replace(".md", ""))
            content_md = post.content
            content_html = markdown.markdown(content_md)
            text = content_html.replace("<p>", "").replace("</p>", "").strip()
            date = post.get("date", datetime.now())

            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date)
                except Exception:
                    date = datetime.now()
            date_path = date.strftime("%Y/%m/%d")
            url_title = title.replace(" ", "-").replace("/", "-")
            full_url = f"{BASE_URL}/{date_path}/{url_title}/"

            # 提取一级标题
            main_heading = extract_main_heading(content_md)

            embedding = get_embedding(text[:5000])
            vector_store.append({
                "title": title,
                "text": text[:5000],
                "path": filepath,
                "url": full_url,
                "embedding": embedding
            })

            # 保存映射
            if main_heading:
                mapping_table.append({
                    "main_heading": main_heading,
                    "title": title,
                    "permalink": full_url
                })

    with open(VECTOR_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(vector_store, f, ensure_ascii=False, indent=2)

    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping_table, f, ensure_ascii=False, indent=2)

    print(f"✅ 向量库已保存到 {VECTOR_STORE_PATH}")
    print(f"✅ 标题映射表已保存到 {MAPPING_PATH}")

if __name__ == "__main__":
    build_vector_store()
