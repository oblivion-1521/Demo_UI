import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# 读取同目录下的 index.html
@app.get("/")
async def get():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    file_path = "input.txt"
    
    # 如果文件不存在，先创建一个初始文件
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("0")

    last_val = None
    try:
        while True:
            # 高频检测文件内容变化
            try:
                #[修复] 加上 utf-8-sig，避免 Windows 编辑器保存带来的 BOM 字符导致 isdigit() 失败
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    content = f.read().strip()
                    # 只要内容是数字，且发生了变化，就推流给前端
                    if content and content.isdigit():
                        val = int(content)
                        if val != last_val:
                            await websocket.send_text(str(val))
                            last_val = val
            except Exception as e:
                pass # 忽略读取冲突等临时错误
            
            # 100ms 检查一次（10Hz），对于前端体验已经足够实时
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print("Client disconnected")