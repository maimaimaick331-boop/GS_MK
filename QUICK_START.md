# 快速参考卡

## 🚀 快速启动

### Windows (两个终端)

**终端1 - 后端:**
```powershell
.\start.bat
```

**终端2 - 前端:**
```powershell
.\frontend-start.bat
```

**访问:** http://localhost:8000

### Linux/Mac

```bash
# 终端1
./start.sh

# 终端2
cd frontend && python3 -m http.server 8000
```

---

## 📍 关键文件位置

| 文件 | 位置 | 说明 |
|------|------|------|
| 后端 | `backend/app.py` | Flask API服务器 |
| 前端 | `frontend/index.html` | 主页面 |
| 数据库 | `data/silver_gold.db` | SQLite数据库 |
| 配置 | `backend/config.py` | 配置文件 |
| 采集器 | `backend/data_collector.py` | 数据采集模块 |

---

## 🔗 API端点速查

### 数据采集
- `POST /api/collect` - 手动采集

### COMEX库存
- `GET /api/comex/warehouse` - 历史数据
- `GET /api/comex/latest` - 最新数据

### 价格
- `GET /api/price/latest` - 所有市场最新
- `GET /api/price/all` - 所有历史数据
- `GET /api/price/by-market/London` - 伦敦市场

### 分析
- `GET /api/analytics` - 分析数据
- `GET /api/analytics/summary` - 摘要

---

## 🛠️ 常用命令

### 后端开发
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python models.py

# 启动服务器
python app.py

# 手动采集数据
python -c "from data_collector import collect_all_data; collect_all_data()"

# 启动定时采集
python scheduler.py
```

### 数据库管理
```bash
cd backend

# 备份数据库
python db_manager.py backup

# 查看统计信息
python db_manager.py stats

# 清理旧日志 (90天)
python db_manager.py cleanup-logs --days 90

# 清理旧数据 (365天)
python db_manager.py cleanup-data --days 365

# 优化数据库
python db_manager.py optimize

# 导出数据
python db_manager.py export comex_warehouse
```

---

## 🐛 故障排查

| 问题 | 解决方案 |
|------|---------|
| CORS错误 | 确保Flask启用CORS: `CORS(app)` |
| 端口被占用 | `netstat -ano \| findstr :5000` (Win) |
| 导入错误 | `pip install -r requirements.txt` |
| 数据库锁定 | 重启服务器或删除`.db-journal`文件 |
| 图表不显示 | 检查Chart.js是否加载，查看浏览器控制台 |

---

## 📊 前端功能

| 功能 | 位置 |
|------|------|
| 实时概览 | 概览标签 |
| 库存趋势 | COMEX库存标签 |
| ETF持仓 | ETF持仓标签 |
| 市场对比 | 市场价格标签 |
| 投资观点 | 投资分析标签 |

---

## 🔐 安全检查清单

- [ ] 更改默认密钥（如适用）
- [ ] 启用HTTPS
- [ ] 配置CORS仅允许信任域名
- [ ] 添加速率限制
- [ ] 定期备份数据库
- [ ] 监控日志文件

---

## 📈 性能优化建议

1. **缓存**: 使用Redis缓存热数据
2. **数据库**: 定期运行优化 `python db_manager.py optimize`
3. **API**: 限制返回记录数，使用分页
4. **前端**: 实现本地缓存，减少API调用

---

## 📞 获取帮助

查看完整文档: `README.md`
部署指南: `DEPLOYMENT.md`

---

**更新日期:** 2026年2月3日
