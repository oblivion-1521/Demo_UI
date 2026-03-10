from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

# 1. 启动时读取数据
df = pd.read_csv('data.csv')
data_list = df.iloc[:, 1].tolist() 

pointer = 0         # 用来遍历波形数据的指针
request_counter = 0 # 用来计算时间的计数器（每0.1秒加1）

# 网页路由：当在浏览器输入网址时，返回 index.html 文件的内容
@app.get("/")
async def get_webpage():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# 数据接口：前端每隔几百毫秒就会偷偷调用一次这个接口
@app.get("/api/get_data")
async def get_sensor_data():
    global pointer, request_counter
    
    # 1. 获取波形数据并移动指针
    val = float(data_list[pointer])
    pointer = (pointer + 1) % len(data_list)
    
    # 2. 计算当前属于哪个疲劳阶段 (0-300: 正常, 300-400: 中度, 400-600: 重度)
    cycle_position = request_counter % 600
    
    if cycle_position < 300:       # 前 30 秒
        fatigue_level = 0
    elif cycle_position < 400:     # 中间 10 秒
        fatigue_level = 1
    else:                          # 后 20 秒
        fatigue_level = 2
        
    request_counter += 1
    
    # 3. 把波形数值和疲劳状态一起打包发给前端
    return {
        "value": val,
        "fatigue": fatigue_level
    }