# 部署检查清单

## ✅ 部署前检查

### 环境检查
- [ ] Python 3.7+ 已安装
- [ ] pip 已安装
- [ ] Node.js（可选，如需额外工具）

### 后端检查
- [ ] requirements.txt 中所有依赖可用
- [ ] SQLite3 可用
- [ ] Flask 应用可正常启动
- [ ] 数据库初始化成功

### 前端检查
- [ ] HTML/CSS/JS 文件完整
- [ ] Chart.js 库可正常加载
- [ ] API 端点配置正确

### 网络检查
- [ ] 防火墙开放必要端口 (5000, 8000)
- [ ] CORS 配置正确
- [ ] 跨域请求可正常进行

## 🚀 部署步骤

### 1. 本地测试
```bash
# 测试后端
cd backend
pip install -r requirements.txt
python models.py
python app.py

# 测试前端（新终端）
cd frontend
python -m http.server 8000

# 验证
# 后端: curl http://localhost:5000/api/health
# 前端: http://localhost:8000
```

### 2. 服务器部署
```bash
# 上传文件到服务器
scp -r Gold&Silver/ user@server:/var/www/

# SSH 登录服务器
ssh user@server

# 部署后端
cd /var/www/Gold&Silver/backend
pip install -r requirements.txt
nohup python app.py > app.log 2>&1 &

# 配置前端（使用Nginx）
# 更新 /etc/nginx/sites-available/default
# 指向 /var/www/Gold&Silver/frontend
```

### 3. 监控和维护
```bash
# 检查后端进程
ps aux | grep python

# 查看后端日志
tail -f /var/www/Gold&Silver/backend/app.log

# 清理数据库
sqlite3 /var/www/Gold&Silver/data/silver_gold.db "DELETE FROM data_log WHERE created_at < date('now', '-30 days');"
```

## 🔍 故障排查

### 问题: 后端无法启动
```bash
# 检查端口占用
netstat -lntp | grep 5000

# 杀死占用进程
kill -9 <PID>

# 检查Python版本
python --version

# 检查依赖
pip list | grep Flask
```

### 问题: 前端无法连接后端
```javascript
// 在浏览器控制台检查
fetch('http://localhost:5000/api/health')
  .then(r => r.json())
  .then(d => console.log(d))
  .catch(e => console.error(e))

// 检查CORS错误
// 解决方案: 后端添加 CORS(app)
```

### 问题: 数据库锁定
```bash
# 重启SQLite
sqlite3 data/silver_gold.db "PRAGMA journal_mode=WAL;"

# 清理锁定文件
rm -f data/silver_gold.db-journal
```

## 📊 性能优化

### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_date ON comex_warehouse(date);
CREATE INDEX idx_market ON silver_price(market, date);
CREATE INDEX idx_category ON gold_data(category, date);

-- 清理旧数据（定期）
DELETE FROM data_log WHERE created_at < datetime('now', '-90 days');
```

### 2. API缓存
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/price/latest')
@cache.cached(timeout=300)
def get_latest_prices():
    # 5分钟缓存
    ...
```

### 3. 前端优化
```javascript
// 减少API调用频率
const refreshInterval = 5 * 60 * 1000; // 5分钟

// 使用本地存储缓存
localStorage.setItem('lastData', JSON.stringify(data));
const cachedData = JSON.parse(localStorage.getItem('lastData'));
```

## 📈 扩展计划

### Phase 1: 数据源
- [ ] 集成Bloomberg API
- [ ] 集成COMEX官方API
- [ ] 集成LBMA数据源

### Phase 2: 功能扩展
- [ ] 用户认证和权限
- [ ] 数据导出功能 (Excel, CSV, PDF)
- [ ] 自定义报表生成
- [ ] 邮件警报通知
- [ ] 移动App

### Phase 3: 性能提升
- [ ] Redis缓存层
- [ ] 数据库分片
- [ ] CDN部署
- [ ] 微服务架构

### Phase 4: 分析增强
- [ ] 机器学习预测模型
- [ ] 高级图表分析
- [ ] 量化策略模块
- [ ] 风险评估工具

## 🔐 安全加强

- [ ] 添加用户认证 (JWT)
- [ ] API 速率限制
- [ ] 输入验证和清理
- [ ] SQL注入防护
- [ ] HTTPS/SSL配置
- [ ] 定期安全审计

## 📞 联系方式

- 技术支持: support@example.com
- 问题反馈: issues@example.com
- 功能建议: feedback@example.com

---

完成日期: 2026年2月3日
