from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from datetime import datetime  # 新增：为了获取当前时间

app = FastAPI()

# 告诉fastapi开放/static的网址路径，在我的电脑上查找static里的文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. 启动时读取数据
df = pd.read_csv('data.csv')

# iloc[:, 1] 的意思是读取所有行（:），以及第2列（索引为1）。
data_list = df.iloc[:, 1].tolist() 

# ===== 读取心率和呼吸率 =====
# 先假设读取重复的数据，后面再进行修改，现在先这样写，不要动。
try:
    hr_list = df.iloc[:, 1].tolist()  # 获取心率 (Heart Rate)
    rr_list = df.iloc[:, 1].tolist()  # 获取呼吸率 (Respiration Rate)
except IndexError:
    # 这是一个保护机制如果找不到列，就先用假数据填充满，保证程序能跑起来。
    print("警告: CSV 文件中没有找到心率和呼吸率所在的列，正在使用默认值。")
    hr_list = [75] * len(data_list)   # 假数据：心率全部为 75
    rr_list = [16] * len(data_list)   # 假数据：呼吸率全部为 16
# =================================

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
    
    # 1. 获取波形数据、心率、呼吸率并移动指针
    val = float(data_list[pointer])
    
    # 获取对应指针位置的心率和呼吸率，转换成整数
    current_hr = int(hr_list[pointer])
    current_rr = int(rr_list[pointer])
    
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
    
    # ===== 新增：获取当前的真实时间 =====
    # datetime.now() 获取当前电脑的时间，strftime("%H:%M:%S") 把时间格式化成 "14:05:30" 这样的字符串
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # 3. 把波形数值、疲劳状态、心率、呼吸率、时间一起打包发给前端
    return {
        "value": val,
        "fatigue": fatigue_level,
        "heart_rate": current_hr, # 把心率传给前端
        "resp_rate": current_rr,  # 把呼吸率传给前端
        "time": current_time      # 把时间传给前端
    }