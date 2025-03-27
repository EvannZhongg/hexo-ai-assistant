# hexo-ai-assistant

[博客用户浏览器] 
     ↓  访问
[chat.html 页面中 JS 调用] 
     ↓ fetch
https://hexo-ai-assistant.evanzhong.workers.dev       ← Cloudflare Worker 公网中转地址
     ↓ HTTP 代理转发
https://7b39-49-72-58-214.ngrok-free.app/ask          ← 你本地服务穿透后的公网地址（Ngrok）
     ↓ 实际请求到
http://localhost:5000/ask                             ← 你运行 main.py 的本地 Flask/FastAPI 模型服务
