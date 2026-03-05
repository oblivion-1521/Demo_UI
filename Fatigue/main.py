from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import random
import math
import time
import pandas as pd

app = FastAPI()

# --- 新增：加载数据并初始化指针 ---
# 在服务器启动时读取文件（不要在接口函数里读取，否则会极慢）
df = pd.read_csv('data.csv')
# 假设你的 CSV 第一列是数据，将其转化为 list 方便索引
data_list = df.iloc[:, 1].tolist() 
# 定义一个全局变量作为“指针”，记录当前读到哪一行了
pointer = 0

# 1. 网页路由：当你在浏览器输入网址时，返回 index.html 文件的内容
@app.get("/")
async def get_webpage():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# 2. 数据接口：前端每隔几百毫秒就会偷偷调用一次这个接口
@app.get("/api/get_data")
async def get_sensor_data():
    global pointer # 声明我们要修改全局变量 pointer
    
    # 获取当前数据
    val = float(data_list[pointer])
    
    # 移动指针，如果读到末尾，则循环回到开头
    pointer = (pointer + 1) % len(data_list)
    
    return {"value": val}