# API 端点文档 - 官方数据集成

## 基础信息

- **服务器地址**: http://localhost:5000
- **数据格式**: JSON
- **字符编码**: UTF-8
- **CORS支持**: 启用

---

## API 端点

### 1. 健康检查

```http
GET /api/health
```

**描述**: 检查API服务器状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T17:08:30.123456",
  "service": "Silver & Gold Market Data API"
}
```

---

### 2. 白银和黄金价格 (来自 Metals.Live API)

```http
GET /api/price/latest
```

**描述**: 获取最新的白银和黄金价格（来自官方Metals.Live API）

**数据源**:
- 📍 Metals.Live Official API
- 🔄 实时更新
- 📊 支持多种货币

**响应示例**:
```json
{
  "success": true,
  "source": "Metals.Live API",
  "data": {
    "silver": {
      "usd": 31.45,
      "cny": 223.30,
      "gbp": 24.85,
      "change_24h": 0.15,
      "change_percent": 0.48
    },
    "gold": {
      "usd": 2050.00,
      "cny": 14555.00,
      "gbp": 1620.00,
      "change_24h": 10.50,
      "change_percent": 0.51
    },
    "markets": {
      "London": {
        "market": "London Metal Exchange (LME)",
        "spot_price": 31.45,
        "futures_price": 31.87,
        "premium": 1.34,
        "premium_type": "Premium"
      },
      "Shanghai": {
        "market": "Shanghai Futures Exchange (SHFE)",
        "spot_price": 242.50,
        "futures_price": 241.20,
        "premium": -1.30,
        "premium_type": "Backwardation"
      },
      "Comex": {
        "market": "New York COMEX (CME)",
        "spot_price": 31.50,
        "futures_price": 31.82,
        "premium": 1.02,
        "premium_type": "Contango"
      }
    }
  }
}
```

**字段说明**:
- `usd`: 美元价格 (每盎司)
- `cny`: 人民币价格 (按当前汇率转换)
- `gbp`: 英镑价格
- `change_24h`: 24小时价格变化
- `change_percent`: 24小时涨跌百分比
- `spot_price`: 现货价格
- `futures_price`: 期货价格
- `premium`: 溢价 (正数) 或贴水 (负数)
- `premium_type`: 市场类型

---

### 3. ETF 持仓数据 (来自 Yahoo Finance API)

```http
GET /api/etf/latest
```

**描述**: 获取白银和黄金相关ETF的实时数据

**数据源**:
- 📍 Yahoo Finance Official API
- 🔄 市场实时数据（交易时间）
- 📊 包含5个主要ETF

**响应示例**:
```json
{
  "success": true,
  "source": "Yahoo Finance API",
  "data": [
    {
      "symbol": "SLV",
      "name": "iShares Silver Trust",
      "category": "Silver ETF",
      "price": 31.50,
      "change": 0.15,
      "changePercent": 0.48,
      "volume": 15000000,
      "marketCap": 10000000000,
      "52WeekHigh": 34.65,
      "52WeekLow": 28.35
    },
    {
      "symbol": "PSLV",
      "name": "Sprott Physical Silver Trust",
      "category": "Physical Silver",
      "price": 12.85,
      "change": 0.10,
      "changePercent": 0.78,
      "volume": 5000000,
      "marketCap": 3000000000,
      "52WeekHigh": 14.20,
      "52WeekLow": 11.50
    },
    {
      "symbol": "GLD",
      "name": "SPDR Gold Shares",
      "category": "Gold ETF",
      "price": 198.50,
      "change": 0.50,
      "changePercent": 0.25,
      "volume": 12000000,
      "marketCap": 80000000000,
      "52WeekHigh": 218.40,
      "52WeekLow": 175.20
    }
  ]
}
```

**支持的ETF**:
| 代码 | 名称 | 类别 | 描述 |
|------|------|------|------|
| SLV | iShares Silver Trust | 白银ETF | 追踪白银现货价格 |
| PSLV | Sprott Physical Silver Trust | 实物白银 | 持有实物白银 |
| AGX | iShares Global Silver & Metals | 金属混合 | 白银和其他贵金属 |
| GLD | SPDR Gold Shares | 黄金ETF | 追踪黄金现货价格 |
| IAU | iShares Gold Trust | 黄金ETF | 追踪黄金现货价格 |

---

### 4. COMEX 库存数据 (来自 COMEX/Quandl API)

```http
GET /api/comex/latest
```

**描述**: 获取COMEX官方白银库存数据

**数据源**:
- 📍 COMEX Official / Quandl CFTC Data
- 🔄 每周更新（COMEX官方数据）
- 📊 用于评估白银市场供应情况

**响应示例**:
```json
{
  "success": true,
  "source": "COMEX Official / Quandl API",
  "data": {
    "date": "2026-02-03",
    "total_oz": 442.48,
    "eligible_oz": 317.04,
    "registered_oz": 125.44,
    "total_tonnes": 13.77,
    "change_24h": -0.50,
    "unit": "Million troy ounces"
  }
}
```

**字段说明**:
- `total_oz`: 总库存 (百万盎司)
- `eligible_oz`: 合格白银库存 (可用于交割)
- `registered_oz`: 注册白银库存 (已分配)
- `total_tonnes`: 总库存 (公制吨)
- `change_24h`: 24小时库存变化 (百万盎司)

**重要指标**:
- **合格白银比例** = eligible_oz / total_oz
  - > 70%: 市场供应充足
  - 50-70%: 供应正常
  - < 50%: 供应紧张

---

### 5. 手动数据采集

```http
POST /api/collect
```

**描述**: 立即触发数据采集任务（从所有官方API获取最新数据）

**请求体**: 无需请求体

**响应示例**:
```json
{
  "success": true,
  "message": "Data collection from real APIs completed",
  "timestamp": "2026-02-03T17:08:35.123456",
  "data_sources": [
    "Metals.Live (Silver & Gold Prices)",
    "Yahoo Finance (ETF Data)",
    "COMEX/Quandl (Warehouse Stocks)",
    "World Bank (Economic Indicators)",
    "Multiple Exchanges (LME, SHFE, COMEX)"
  ]
}
```

**使用场景**:
- 需要最新数据时手动触发
- 用于测试数据采集功能
- 验证API连接状态

---

## 官方API集成详情

### Metals.Live API
```
URL: https://api.metals.live/v1/spot/{silver|gold}
更新频率: 实时
免费额度: 100请求/天
状态: ✅ 完全集成
```

### Yahoo Finance API
```
URL: https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}
更新频率: 实时 (交易时间)
免费额度: 无限制
状态: ✅ 完全集成
```

### COMEX/Quandl API
```
URL: https://www.quandl.com/api/v3/datasets/CFTC/SI_FO_L_ALL
更新频率: 周度
免费额度: 200请求/天
状态: ✅ 完全集成
```

### 世界银行 API
```
URL: https://api.worldbank.org/v2/
更新频率: 年度
免费额度: 无限制
状态: ✅ 完全集成
```

---

## 使用示例

### JavaScript (前端)

```javascript
// 获取最新价格
fetch('http://localhost:5000/api/price/latest')
  .then(res => res.json())
  .then(data => {
    console.log('White Silver Price:', data.data.silver.usd, 'USD');
    console.log('Gold Price:', data.data.gold.usd, 'USD');
  });

// 获取ETF数据
fetch('http://localhost:5000/api/etf/latest')
  .then(res => res.json())
  .then(data => {
    data.data.forEach(etf => {
      console.log(`${etf.symbol}: $${etf.price}`);
    });
  });

// 触发数据采集
fetch('http://localhost:5000/api/collect', { method: 'POST' })
  .then(res => res.json())
  .then(data => console.log(data.message));
```

### Python

```python
import requests

# 获取价格数据
response = requests.get('http://localhost:5000/api/price/latest')
prices = response.json()
print(f"Silver: ${prices['data']['silver']['usd']}")

# 获取ETF数据
response = requests.get('http://localhost:5000/api/etf/latest')
etfs = response.json()
for etf in etfs['data']:
    print(f"{etf['symbol']}: ${etf['price']}")

# 手动采集
response = requests.post('http://localhost:5000/api/collect')
print(response.json()['message'])
```

### cURL

```bash
# 获取健康状态
curl http://localhost:5000/api/health

# 获取价格
curl http://localhost:5000/api/price/latest

# 获取ETF数据
curl http://localhost:5000/api/etf/latest

# 获取COMEX库存
curl http://localhost:5000/api/comex/latest

# 触发数据采集
curl -X POST http://localhost:5000/api/collect
```

---

## 错误响应

如果请求失败，API会返回错误响应：

```json
{
  "success": false,
  "error": "Description of the error",
  "timestamp": "2026-02-03T17:08:35.123456"
}
```

---

## 数据刷新频率

| 数据类型 | 来源 | 频率 | 延迟 |
|---------|------|------|------|
| 白银价格 | Metals.Live | 实时 | < 1分钟 |
| 黄金价格 | Metals.Live | 实时 | < 1分钟 |
| ETF价格 | Yahoo Finance | 15分钟 | 15分钟 |
| 库存数据 | COMEX/Quandl | 每周 | 1-3天 |
| 市场数据 | 各交易所 | 实时 | < 1分钟 |
| 经济指标 | World Bank | 每年 | 3-6个月 |

---

## 对接到自己的网站

### 步骤1: 获取数据
```html
<script>
  // 定期获取数据
  async function fetchData() {
    const response = await fetch('http://localhost:5000/api/price/latest');
    const data = await response.json();
    return data;
  }
  
  // 每5分钟刷新一次
  setInterval(fetchData, 5 * 60 * 1000);
</script>
```

### 步骤2: 显示数据
```html
<div id="silver-price"></div>

<script>
  fetch('http://localhost:5000/api/price/latest')
    .then(res => res.json())
    .then(data => {
      const price = data.data.silver.usd;
      const cny = data.data.silver.cny;
      document.getElementById('silver-price').innerHTML = 
        `White Silver: $${price} / ¥${cny}`;
    });
</script>
```

### 步骤3: 部署
1. 在你的服务器上运行本系统
2. 更新前端的API URL为你的服务器地址
3. 设置CORS（如需跨域）

---

## 常见问题

**Q: API是否支持跨域请求?**
A: 是的，已启用CORS，支持所有来源的跨域请求。

**Q: 数据更新频率是多少?**
A: 后台自动每小时更新一次，也可通过 `/api/collect` 手动触发。

**Q: 官方API不可用时会怎样?**
A: 系统会自动使用基于官方数据的模拟数据，确保应用持续可用。

**Q: 如何获得更高的API速率限制?**
A: 可以为Metals.Live和Quandl配置付费API密钥。

---

## 技术文档

详见 `OFFICIAL_API_INTEGRATION.md` 了解技术细节。

---

**最后更新**: 2026年2月3日
**API版本**: 1.0.0
**状态**: ✅ 完全可用
