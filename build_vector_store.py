import os
import json
import markdown
import frontmatter
from embedder import get_embedding, load_config
from datetime import datetime
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
config = load_config()

POST_PATH = config["paths"]["blog_post_dir"]
OUTPUT_PATH = config["paths"]["vector_store"]
MAPPING_PATH = config["paths"]["title_mapping"]
BASE_URL = config["blog"]["base_url"]
MAX_CHARS = config["embedding"]["max_characters"]

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

            main_heading = extract_main_heading(content_md)

            embedding = get_embedding(text[:MAX_CHARS])
            vector_store.append({
                "title": title,
                "text": text[:MAX_CHARS],
                "path": filepath,
                "url": full_url,
                "embedding": embedding
            })

            if main_heading:
                mapping_table.append({
                    "main_heading": main_heading,
                    "title": title,
                    "permalink": full_url
                })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(vector_store, f, ensure_ascii=False, indent=2)
    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping_table, f, ensure_ascii=False, indent=2)

    print(f"✅ 向量库已保存到 {OUTPUT_PATH}")
    print(f"✅ 标题映射表已保存到 {MAPPING_PATH}")

if __name__ == "__main__":
    build_vector_store()
