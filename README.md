# 金银市场数据分析平台 - 部署指南 (V1.5)

## 📋 项目概述

这是一个完整的金银市场数据采集和分析平台，集成了多个**官方API数据源**，包括：
- **后端服务** - Python API服务器，**实时官方数据采集**和存储
- **前端网站** - 现代化的Web界面，实时数据展示
- **数据库** - SQLite数据库，存储历史数据
- **自动采集** - 定时数据采集脚本

### 🌐 官方数据源
✅ **Metals.Live API** - 实时白银和黄金价格
✅ **Yahoo Finance API** - ETF持仓和市场数据
✅ **COMEX/Quandl** - 仓库库存数据
✅ **多个交易所API** - LME, SHFE, COMEX市场数据
✅ **World Bank API** - 经济指标数据

## 📁 项目结构

```
Gold&Silver/
├── backend/                      # 后端服务
│   ├── simple_server.py         # 轻量级API服务器（无需pip依赖）
│   ├── real_api_collector.py    # 官方API数据采集模块 ⭐新增
│   ├── app.py                   # Flask API服务器
│   ├── config.py                # 配置文件
│   ├── models.py                # 数据模型
│   ├── data_collector.py        # 数据采集模块
│   ├── test_real_api.py         # API测试脚本
│   └── requirements.txt          # 依赖包列表
├── frontend/                     # 前端网站
│   ├── index.html               # 主页
│   ├── start.html               # 启动中心（一键启动）
│   ├── js/
│   │   ├── api.js               # API交互模块
│   │   └── main.js              # 主程序脚本
│   └── package.json             # 项目配置
├── data/                        # 数据存储
│   ├── silver_gold.db           # SQLite数据库
│   └── raw/                     # 原始审计报表 (XLS/XLSX) ⭐新增 P0
├── OFFICIAL_API_INTEGRATION.md  # 官方API集成文档
├── one-click-start.bat          # 一键启动脚本 ⭐新增
├── quick-start.bat              # 快速启动脚本
├── start.bat                    # Windows启动脚本
├── start.sh                     # Linux/Mac启动脚本
└── README.md                    # 本文档
```

## 🚀 快速启动

### Windows用户 - 最简单的方式

#### 一键启动（推荐）
```powershell
# 运行一键启动脚本
.\one-click-start.bat

# 脚本会自动：
# 1. 启动API服务器 (端口 5000)
# 2. 启动前端服务器 (端口 8000)
# 3. 打开浏览器并访问应用
```

#### 或使用启动中心
```powershell
# 启动后访问
http://localhost:8000/start.html

# 点击"启动应用程序"按钮自动启动并配置所有服务
```

#### 2. 在另一个终端启动前端
```powershell
# 方法1: 使用批处理脚本
.\frontend-start.bat

# 方法2: 手动启动
cd frontend
python -m http.server 8000
```

#### 3. 在浏览器访问
```
http://localhost:8000
```

### Linux/Mac用户

```bash
# 启动后端
chmod +x start.sh
./start.sh

# 在另一个终端启动前端
cd frontend
python3 -m http.server 8000
```

## 🔧 配置说明

### 后端配置 (backend/config.py)

```python
# 数据库位置
DB_PATH = 'data/silver_gold.db'

# API更新间隔（秒）
DATA_UPDATE_INTERVAL = 3600  # 1小时

# Flask配置
FLASK_ENV = 'development'
DEBUG = True
```

### 前端配置 (frontend/js/api.js)

```javascript
const API_BASE = 'http://localhost:5000/api';
```

## 📊 API接口

### 数据采集

**POST /api/collect**
- 手动触发数据采集
- 返回: 采集结果状态

### COMEX库存

**GET /api/comex/warehouse?days=30**
- 获取COMEX仓库库存历史数据
- 参数: days (天数，默认30)

**GET /api/comex/latest**
- 获取最新COMEX库存数据

### ETF持仓

**GET /api/etf/holdings?days=30**
- 获取ETF持仓历史数据

**GET /api/etf/latest**
- 获取最新ETF持仓数据

### 白银价格

**GET /api/price/latest**
- 获取各市场最新价格

**GET /api/price/all?days=30**
- 获取所有市场价格历史

**GET /api/price/by-market/<market>?days=30**
- 获取特定市场价格
- market: London, Shanghai, Comex

### 分析数据

**GET /api/analytics?category=<category>&days=30**
- 获取投资分析数据
- category: 认知层级, 逻辑层级, 数据层级, 风险层级

**GET /api/analytics/summary**
- 获取分析摘要

### 系统信息

**GET /api/health**
- 健康检查

**GET /api/logs?limit=50**
- 获取采集日志

## 📈 功能特性

### 1. 实时数据展示
- COMEX白银库存趋势
- 白银ETF持仓变化
- 多市场价格对比（伦敦、上海、COMEX）
- 现货价格与期货价格差异

### 2. 投资分析
- **认知层级**: 货币史视角、技术分析、全球化判断、势力预测
- **逻辑层级**: 白银驱动、赤字、资源竞争、金融逻辑
- **数据层级**: 交易数据、库存变化、中心互动、微观交易
- **风险层级**: 白银增量、ETF狂抛、债务危机、资源战略

### 3. 数据管理
- SQLite数据库存储
- 自动采集日志
- 历史数据查询
- 数据可视化图表

## 🔄 自动采集设置

### Python版本（使用APScheduler）

修改 `backend/data_collector.py`，添加定时采集：

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(collect_all_data, 'interval', hours=1)
scheduler.start()
```

### 使用任务计划（Windows）

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每小时
4. 操作：运行程序 `python backend/data_collector.py`

### 使用Cron（Linux/Mac）

```bash
# 每小时执行一次
0 * * * * cd /path/to/Gold&Silver && python3 backend/data_collector.py
```

## 📱 前端使用指南

### 导航栏
- **概览** - 仪表板，显示最新数据
- **COMEX库存** - 库存趋势图表和历史数据
- **ETF持仓** - ETF持仓量变化
- **市场价格** - 各市场价格对比
- **投资分析** - 四大投资观点分析

### 操作按钮
- **📊 更新数据** - 手动触发后端采集
- **🔄 刷新** - 刷新前端数据

### 数据筛选
- 支持按时间范围筛选（默认30天）
- 支持按市场、ETF、分类筛选

## 🌐 部署到生产环境

### 使用Gunicorn (推荐)

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

### Docker部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY frontend/ static/

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

构建和运行：

```bash
docker build -t silver-gold-api .
docker run -p 5000:5000 silver-gold-api
```

## 🔒 安全建议

1. **环境变量配置**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   API_KEY = os.getenv('API_KEY')
   ```

2. **CORS配置**
   ```python
   CORS(app, resources={r"/api/*": {"origins": ["https://yourdomain.com"]}})
   ```

3. **API认证**
   ```python
   @app.route('/api/protected')
   def protected():
       token = request.headers.get('Authorization')
       if not verify_token(token):
           return jsonify({'error': 'Unauthorized'}), 401
   ```

4. **HTTPS设置**
   - 使用SSL证书
   - 自动重定向HTTP到HTTPS

## 📝 数据源集成

当前使用的是示例数据。要集成真实数据源：

### 1. Bloomberg API
```python
import Bloomberg

def get_bloomberg_data():
    # 连接Bloomberg数据
    session = Bloomberg.BloombergSession()
    # 获取白银现货价格
    price = session.get_field('SLVUSD:CUR', 'LAST_PRICE')
```

### 2. COMEX官方数据
```python
def scrape_comex_warehouse():
    # 爬取COMEX仓库数据
    url = 'https://www.cmegroup.com/market-data/datamine/'
    # 解析HTML或JSON API
```

### 3. 其他数据源
- LBMA伦敦金银交易
- 上海期货交易所API
- 各类金融数据API服务

## 🐛 常见问题

### Q: 跨域问题 (CORS Error)
**A:** 确保后端启用了CORS：
```python
from flask_cors import CORS
CORS(app)
```

### Q: 数据库被锁定
**A:** 检查多个进程是否访问同一数据库：
```python
sqlite3 data/silver_gold.db ".timeout 5000"
```

### Q: 图表不显示
**A:** 检查浏览器控制台是否有JS错误，确保Chart.js库已加载

### Q: API响应缓慢
**A:** 
1. 添加缓存机制
2. 使用数据库索引
3. 限制查询数据量

## 📞 支持和反馈

如有问题或建议，请：
1. 检查日志文件
2. 查看浏览器控制台错误
3. 验证API是否正常运行

## 🕒 版本历史 (Version History)

### **V1.5 (2026-02-04)**
- **核心**: 交付 P0 级库存审计闭环机制。
- **审计**:
  - 原始报表持久化存储与 SHA256 指纹校验。
  - COMEX 勾稽关系校验 (`Total = E + R`)。
  - LME 字段口径透明化与 STALE 过期标记。
  - 前端 Hover 审计元数据展示。
- **修复**:
  - 全线修复 `requirements.txt` 缺失依赖导致的断流问题。
  - 修正 EFP 铜价单位转换与双源校验逻辑。
  - 解决 `models.py` 导入路径异常。

### **保本V1.1 (2026-02-04)**
- **功能**: EFP 实时监测与异常处理加固。
- **改进**:
  - 铜价单位自动转换：后端对齐美分/美元，前端对齐 ton/lb (`1 ton = 2204.62 lb`)。
  - 解决 Comex 铜双源校验“数据错误”拦截。
  - 异常提示精细化（显示 NY/London 缺失）。
  - 后端 API 根路径引导页。
  - COMEX/London 字段映射对齐。

## 📄 许可证

MIT License

---

**最后更新**: 2026年2月4日
**版本**: 1.5
