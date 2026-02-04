# 对接到自己的网站 - 集成指南

## 概述

本系统提供完整的金银市场数据API接口，可以轻松集成到你自己的网站。所有数据均来自官方API源，实时更新，准确可靠。

---

## 快速开始

### 方式1: 直接嵌入iframe

最简单的方式，无需任何后端改动：

```html
<!DOCTYPE html>
<html>
<head>
    <title>我的网站 + 金银数据</title>
</head>
<body>
    <h1>欢迎来到我的网站</h1>
    
    <!-- 嵌入金银数据面板 -->
    <iframe src="http://your-server:8000" 
            width="100%" 
            height="800px"
            frameborder="0"
            style="border: none; border-radius: 8px;">
    </iframe>
</body>
</html>
```

---

## 方式2: 通过API调用（推荐）

### 步骤1: 启动API服务器

在你的服务器上运行：
```bash
python backend/simple_server.py
# 服务运行在 http://localhost:5000
```

### 步骤2: 在你的网站中调用API

#### HTML示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>我的网站 - 金银价格</title>
    <style>
        .price-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 20px;
        }
        .price-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>金银市场数据</h1>
    
    <div class="price-card">
        <h2>白银价格</h2>
        <div class="price-value" id="silver-usd">加载中...</div>
        <p id="silver-cny"></p>
        <p style="font-size: 0.9em; opacity: 0.8;">数据来源: Metals.Live API</p>
    </div>
    
    <div class="price-card">
        <h2>黄金价格</h2>
        <div class="price-value" id="gold-usd">加载中...</div>
        <p id="gold-cny"></p>
        <p style="font-size: 0.9em; opacity: 0.8;">数据来源: Metals.Live API</p>
    </div>
    
    <script>
        // 从API获取数据
        async function loadPrices() {
            try {
                const response = await fetch('http://localhost:5000/api/price/latest');
                const data = await response.json();
                
                if (data.success) {
                    // 更新白银价格
                    document.getElementById('silver-usd').textContent = 
                        `$${data.data.silver.usd}/oz`;
                    document.getElementById('silver-cny').textContent = 
                        `¥${data.data.silver.cny}`;
                    
                    // 更新黄金价格
                    document.getElementById('gold-usd').textContent = 
                        `$${data.data.gold.usd}/oz`;
                    document.getElementById('gold-cny').textContent = 
                        `¥${data.data.gold.cny}`;
                }
            } catch (error) {
                console.error('获取价格失败:', error);
                document.getElementById('silver-usd').textContent = '网络错误';
            }
        }
        
        // 页面加载时获取数据
        loadPrices();
        
        // 每5分钟自动刷新一次
        setInterval(loadPrices, 5 * 60 * 1000);
    </script>
</body>
</html>
```

---

## 方式3: 使用我们提供的API客户端库

### 在前端项目中使用

```html
<!-- 引入API客户端库 -->
<script src="http://localhost:5000/static/api.js"></script>

<script>
    // 使用API客户端
    const api = new GoldSilverAPI('http://localhost:5000');
    
    api.getLatestPrice().then(data => {
        console.log('Silver:', data.silver);
        console.log('Gold:', data.gold);
    });
    
    api.getETFData().then(data => {
        data.forEach(etf => {
            console.log(`${etf.symbol}: $${etf.price}`);
        });
    });
</script>
```

---

## 方式4: 后端集成

### Node.js/Express

```javascript
// 安装依赖
npm install axios

// 在你的路由中
const axios = require('axios');

app.get('/api/metals', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:5000/api/price/latest');
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 使用
// GET /api/metals
// 返回: { silver: { usd: 31.45, cny: 223.30 }, gold: { ... } }
```

### PHP

```php
<?php
// 获取金银价格
function getGoldSilverPrices() {
    $apiUrl = 'http://localhost:5000/api/price/latest';
    
    $context = stream_context_create([
        'http' => [
            'timeout' => 5
        ]
    ]);
    
    $response = file_get_contents($apiUrl, false, $context);
    return json_decode($response, true);
}

// 使用
$data = getGoldSilverPrices();
echo "Silver: ${$data['data']['silver']['usd']}/oz";
?>
```

### Python Flask

```python
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/api/metals')
def get_metals():
    try:
        response = requests.get('http://localhost:5000/api/price/latest', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
```

---

## 完整示例项目

### HTML + Chart.js 实时图表

```html
<!DOCTYPE html>
<html>
<head>
    <title>金银价格实时图表</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 金银实时数据中心</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>白银价格</h3>
                <div class="stat-value" id="silver-price">加载中...</div>
                <p id="silver-currency">USD</p>
            </div>
            
            <div class="stat-card">
                <h3>黄金价格</h3>
                <div class="stat-value" id="gold-price">加载中...</div>
                <p id="gold-currency">USD</p>
            </div>
            
            <div class="stat-card">
                <h3>COMEX库存</h3>
                <div class="stat-value" id="comex-stock">加载中...</div>
                <p>百万盎司</p>
            </div>
        </div>
        
        <h2>市场数据对比</h2>
        <div class="chart-container">
            <canvas id="priceChart"></canvas>
        </div>
        
        <h2>ETF持仓情况</h2>
        <table id="etf-table" style="width:100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f0f0f0;">
                    <th style="padding:10px; text-align:left;">代码</th>
                    <th style="padding:10px; text-align:left;">名称</th>
                    <th style="padding:10px; text-align:right;">价格</th>
                    <th style="padding:10px; text-align:right;">变化</th>
                </tr>
            </thead>
            <tbody id="etf-body"></tbody>
        </table>
        
        <p style="margin-top:20px; color:#666; font-size:0.9em;">
            数据更新于: <span id="last-update">--:--:--</span>
            | 数据来源: Metals.Live, Yahoo Finance, Quandl, World Bank
        </p>
    </div>
    
    <script>
        // API配置
        const API_BASE = 'http://localhost:5000';
        let priceChart = null;
        
        // 初始化图表
        function initChart() {
            const ctx = document.getElementById('priceChart').getContext('2d');
            priceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: '白银 (USD)',
                            data: [],
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.3
                        },
                        {
                            label: '黄金 (USD, ÷100)',
                            data: [],
                            borderColor: '#f39c12',
                            backgroundColor: 'rgba(243, 156, 18, 0.1)',
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' }
                    },
                    scales: {
                        y: { beginAtZero: false }
                    }
                }
            });
        }
        
        // 更新数据
        async function updateData() {
            try {
                // 获取价格数据
                const priceResp = await fetch(`${API_BASE}/api/price/latest`);
                const priceData = await priceResp.json();
                
                if (priceData.success) {
                    // 更新价格卡片
                    document.getElementById('silver-price').textContent = 
                        `$${priceData.data.silver.usd.toFixed(2)}`;
                    document.getElementById('gold-price').textContent = 
                        `$${priceData.data.gold.usd.toFixed(2)}`;
                    
                    // 更新图表数据
                    if (priceChart.data.labels.length >= 12) {
                        priceChart.data.labels.shift();
                        priceChart.data.datasets[0].data.shift();
                        priceChart.data.datasets[1].data.shift();
                    }
                    
                    const now = new Date();
                    priceChart.data.labels.push(
                        `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`
                    );
                    priceChart.data.datasets[0].data.push(priceData.data.silver.usd);
                    priceChart.data.datasets[1].data.push(priceData.data.gold.usd / 100);
                    priceChart.update();
                }
                
                // 获取COMEX库存
                const comexResp = await fetch(`${API_BASE}/api/comex/latest`);
                const comexData = await comexResp.json();
                if (comexData.success) {
                    document.getElementById('comex-stock').textContent = 
                        comexData.data.total_oz.toFixed(2);
                }
                
                // 获取ETF数据
                const etfResp = await fetch(`${API_BASE}/api/etf/latest`);
                const etfData = await etfResp.json();
                if (etfData.success) {
                    const tbody = document.getElementById('etf-body');
                    tbody.innerHTML = '';
                    etfData.data.forEach(etf => {
                        const row = tbody.insertRow();
                        row.innerHTML = `
                            <td style="padding:10px;">${etf.symbol}</td>
                            <td style="padding:10px;">${etf.name}</td>
                            <td style="padding:10px; text-align:right;">$${etf.price.toFixed(2)}</td>
                            <td style="padding:10px; text-align:right; color:${etf.change >= 0 ? 'green' : 'red'};">
                                ${etf.change >= 0 ? '+' : ''}${etf.change.toFixed(2)} (${etf.changePercent.toFixed(2)}%)
                            </td>
                        `;
                    });
                }
                
                // 更新时间戳
                document.getElementById('last-update').textContent = 
                    new Date().toLocaleTimeString('zh-CN');
                
            } catch (error) {
                console.error('数据更新失败:', error);
            }
        }
        
        // 页面加载时初始化
        initChart();
        updateData();
        
        // 每5分钟更新一次
        setInterval(updateData, 5 * 60 * 1000);
    </script>
</body>
</html>
```

---

## 部署到生产环境

### 步骤1: 部署API服务器

```bash
# 在你的服务器上
cd /var/www/Gold&Silver
python backend/simple_server.py &
```

### 步骤2: 配置反向代理（可选但推荐）

#### Nginx配置

```nginx
# /etc/nginx/sites-available/default

upstream gold_silver_api {
    server localhost:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # API代理
    location /api {
        proxy_pass http://gold_silver_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'Content-Type';
    }
    
    # 前端静态文件
    location / {
        root /var/www/Gold&Silver/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

### 步骤3: 启用HTTPS

```bash
# 使用Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### 步骤4: 在你的网站中使用

```html
<!-- 使用你的域名 -->
<script>
    fetch('https://your-domain.com/api/price/latest')
        .then(res => res.json())
        .then(data => {
            console.log('Silver:', data.data.silver.usd);
        });
</script>
```

---

## 跨域问题解决

### 如果遇到CORS错误

系统已默认启用CORS，但如果还有问题：

#### 方案1: 使用代理服务器（推荐）
见上面的Nginx配置

#### 方案2: 在API端点添加CORS头

在`simple_server.py`中已实现：
```python
self.send_header('Access-Control-Allow-Origin', '*')
self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
```

#### 方案3: 使用JSONP（备选）

```javascript
fetch('http://localhost:5000/api/price/latest?callback=handleData')
    .then(res => res.json())
    .then(data => handleData(data));
```

---

## 性能优化

### 1. 使用CDN缓存
```nginx
location /api/price/latest {
    proxy_pass http://gold_silver_api;
    proxy_cache_valid 200 5m;  # 5分钟缓存
    add_header X-Cache-Status $upstream_cache_status;
}
```

### 2. 启用Gzip压缩
```nginx
gzip on;
gzip_types application/json text/html text/css;
gzip_min_length 1024;
```

### 3. 减少API调用
```javascript
// 使用本地缓存
const cache = {};
const CACHE_TIME = 5 * 60 * 1000;  // 5分钟

async function fetchWithCache(url) {
    const now = Date.now();
    if (cache[url] && (now - cache[url].time) < CACHE_TIME) {
        return cache[url].data;
    }
    
    const data = await fetch(url).then(r => r.json());
    cache[url] = { data, time: now };
    return data;
}
```

---

## 故障排查

### 问题1: 无法连接到API

```bash
# 检查API服务是否运行
curl http://localhost:5000/api/health

# 检查防火墙
sudo ufw allow 5000
```

### 问题2: CORS错误

```javascript
// 使用本服务器作为代理而不是直接调用
// 在你的后端添加代理端点
app.get('/proxy/api/*', (req, res) => {
    fetch('http://localhost:5000' + req.path)
        .then(r => r.json())
        .then(data => res.json(data));
});
```

### 问题3: 数据不更新

```bash
# 手动触发数据采集
curl -X POST http://localhost:5000/api/collect

# 检查后台线程
ps aux | grep python
```

---

## 成功案例

见前面的完整示例项目代码。

---

## 更多资源

- API完整文档: `API_DOCUMENTATION.md`
- 技术实现: `OFFICIAL_API_INTEGRATION.md`
- 系统更新: `SYSTEM_UPDATE_SUMMARY.md`

---

**现在就开始集成吧！** 🚀

有任何问题，请参考API文档或运行测试脚本。
