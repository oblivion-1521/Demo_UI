环境配置：fastapi(后端框架)，uvicorn(运行服务器)，echarts(前端图表库)

- main.py: 建一个服务器，提供两个接口：一个返回HTML页面，一个返回实时数据（波形+疲劳状态）
- index.html: 前端页面，加载ECharts库，画一个实时更新的心电图和显示疲劳状态的文本。

# 整体逻辑框架
uvicorn main:app --host 0.0.0.0 --port 8000

uvicorn 是一个“应用服务器（Application Server）”,会把你的代码作为一个“组件”加载到它自己内部。它会自动解析、实例化并管理你的 app 对象，处理多线程、异步请求队列、网络套接字绑定等底层复杂逻辑。  
main:app 动态导入模块（类似于import main）  
--host 0.0.0.0 表示允许任何网络接口访问这个服务（对外开放）
--port 8000 是在这个服务器上开的一个“特定的门”。  
当在浏览器输入 http://localhost:8000/ 时，浏览器会通过网络协议（HTTP）向这个服务器的8000端口发出请求。服务器会根据请求的路径找到对应的处理函数(get_webpage)，执行它，并把结果返回给浏览器。  

get_webpage 函数会返回 index.html 的内容，浏览器拿到这个 HTML 文档后就会开始解析它，加载里面的 CSS 和 JS 资源. JS 里面

### Step 1: 确定技术栈与环境搭建 (Tech Stack & Setup)
- 后端 (main.py): Python + FastAPI (极简、高性能的Web框架，几行代码就能建个服务器)。  
- 前端 (HTML): HTML + CSS (负责长相) + JavaScript (负责向后端要数据并更新界面)。  
- 可视化图表库: Apache ECharts 或 Chart.js（这两个开源JS库画实时心电图/波形图非常流畅，开箱即用）。  

### Step 2: 准备模拟数据源
- 波形数据：Kaggle – MIT-BIH Arrhythmia Database上随便一个波形。
- 疲劳状态：随便模拟一个
- 细节：
pointer = 0         # 用来遍历波形数据的指针
request_counter = 0 # 用来计算时间的计数器（每0.1秒加1）

### Step 3: 编写后端接口：FastAPI
让前端能够拿到处理好的数据
- 静态页面接口：写一个路由（/），浏览器访问的时候返回HTML页面。
- 数据流接口：路由（/api/get_data）返回实时波形和疲劳。

也可以返回一段JSON数据

```JSON
{
  "waveform_chunk":[0.1, 0.15, 0.4, -0.2, ...], 
  "fatigue_level": 0,
  "temperature": 27.5,
  "battery": 98
}
```
### Step 4: 编写前端页面和排版：HTML
- DOM（文档对象模型）：关键的文字贴上了 id 标签（例如 id="ui-fatigue-status"），方便后面抓取它。
- CSS Flexbox：对齐、留白通过display: flex;自动计算。

# main.py
- 路由：Web 开发里的“分支调度器”。  
当你在浏览器输入 http://localhost:8000/api/get_data 时，由于网址后面跟了不同的路径（Path），服务器需要知道用哪段代码来处理这个请求。
```python
@app.get('/api/get_data')
```
的@app.get('/api/get_data')就是告诉服务器：当收到 /api/get_data 这个路径的请求时，执行下面这个函数（get_data）。  
这里@app.get装饰器就是路由

# index.html
**1. 解析 HTML (<body> 中的标签)**

HTML 是**骨架**。比如 \<div class="card">，浏览器看到这个，就在屏幕上划出一块矩形区域。

**2. 解析 CSS (<\style> 中的代码)**

CSS 是**皮肤**。浏览器看到 .card { background-color: var(--card-bg); border-radius: 8px; }，就会把刚才那个矩形填上底色，并把直角变成圆角。

**3. 执行 JavaScript (<\script> 中的代码) —— 这是核心的动态逻辑！**

JS 是**肌肉和神经**。你的电脑浏览器内置了 V8 引擎（专门运行 JS 语言）。这段代码会在你的 **Windows 的浏览器里** 一直运行，完全脱离了 Python：

```jsx
// JS 代码片段
setInterval(fetchAndUpdateData, 100);
```

这行代码的意思是：**每隔 100 毫秒，执行一次 fetchAndUpdateData 函数。**

在这个函数内部（对应你的 <\script> 标签里）：

1. **发起请求**：let response = await fetch('/api/get_data');
    
    浏览器主动通过网络向 WSL 发起 HTTP 请求。
    
2. **拿到数据**：拿到刚才说的 JSON 字符串并解析出 value 和 fatigue。
3. **驱动 UI**：
    - 更新队列：把 value 塞进 dataQueue 数组（相当于 Python 里的 list）。
    - 调用 myChart.setOption(...)：调用 ECharts（一个很出名的图表库）把数组画成波形图。
    - 判断状态：如果 currentFatigue === 2，JS 就通过 DOM API（如 uiStatus.innerHTML = ...）把屏幕上的字变成红色，内容换成 "Severe Fatigue"。