# 📚 项目索引和导航

## 🎯 快速导航

### 我想要...

**🚀 快速启动项目**
1. Windows 用户: 运行 `start.bat`
2. Linux/Mac 用户: 运行 `start.sh`  
3. 访问 http://localhost:8000
→ 查看 `QUICK_START.md`

**📖 了解项目完整信息**
→ 查看 `README.md`

**🔧 部署到生产环境**
→ 查看 `DEPLOYMENT.md`

**📊 查看项目总结统计**
→ 查看 `PROJECT_SUMMARY.md`

**✅ 验收交付内容**
→ 查看 `DELIVERY_CHECKLIST.md`

**🏗️ 理解项目结构**
→ 查看 `PROJECT_STRUCTURE.txt`

---

## 📂 文件导览

### 🔴 核心文件

#### 后端服务
| 文件 | 行数 | 用途 |
|------|------|------|
| `backend/app.py` | 450 | Flask API服务器 |
| `backend/models.py` | 150 | 数据模型定义 |
| `backend/config.py` | 40 | 配置管理 |
| `backend/data_collector.py` | 350 | 数据采集 |
| `backend/scheduler.py` | 60 | 定时任务 |
| `backend/db_manager.py` | 200 | 数据库工具 |
| `backend/requirements.txt` | - | 依赖列表 |

#### 前端网站
| 文件 | 行数 | 用途 |
|------|------|------|
| `frontend/index.html` | 650 | 主页面 |
| `frontend/js/api.js` | 180 | API客户端 |
| `frontend/js/main.js` | 450 | 主程序 |
| `frontend/package.json` | - | 项目配置 |

#### 启动脚本
| 文件 | 用途 |
|------|------|
| `start.bat` | Windows后端启动 |
| `start.sh` | Linux/Mac启动 |
| `frontend-start.bat` | 前端启动 |

### 🟢 文档文件

| 文档 | 大小 | 内容 |
|------|------|------|
| `README.md` | 20KB | 📖 完整功能文档 |
| `QUICK_START.md` | 8KB | ⚡ 快速参考卡 |
| `DEPLOYMENT.md` | 15KB | 🚀 部署指南 |
| `PROJECT_SUMMARY.md` | 12KB | 📊 项目总结 |
| `DELIVERY_CHECKLIST.md` | 10KB | ✅ 交付清单 |
| `PROJECT_STRUCTURE.txt` | 5KB | 🏗️ 结构说明 |
| `INDEX.md` | 本文件 | 🗺️ 导航索引 |

---

## 🔍 按功能查找

### 我想要启动/部署项目

**本地开发:**
```
查看: QUICK_START.md - "快速启动" 部分
文件: start.bat / start.sh
```

**生产部署:**
```
查看: DEPLOYMENT.md - "部署步骤" 部分
文件: backend/app.py (Gunicorn配置)
```

**Docker部署:**
```
查看: DEPLOYMENT.md - "Docker部署" 部分
创建: Dockerfile (需自建)
```

---

### 我想要理解数据流

**数据采集流程:**
```
查看: backend/data_collector.py
涉及: ComexDataCollector, ETFDataCollector, PriceDataCollector
```

**数据存储:**
```
查看: backend/models.py
表: comex_warehouse, silver_etf, silver_price, gold_data
```

**API调用:**
```
查看: frontend/js/api.js - APIClient 类
方法: getWarehouseData(), getETFData(), getPrices() 等
```

**前端展示:**
```
查看: frontend/js/main.js
函数: loadWarehouseData(), loadETFData(), loadPriceData() 等
```

---

### 我想要添加新功能

**添加新的数据采集器:**
```
1. 参考: backend/data_collector.py
2. 继承: DataCollector 类
3. 实现: collect_xxx_data() 方法
4. 注册: 在 collect_all_data() 中调用
```

**添加新的API端点:**
```
1. 参考: backend/app.py
2. 使用: @app.route() 装饰器
3. 查询: 使用 Session 和模型
4. 返回: JSON 格式
```

**添加新的前端页面:**
```
1. 参考: frontend/index.html
2. 添加: 新的 <div class="tab-content">
3. 创建: 新的标签按钮
4. 实现: 对应的 JavaScript 函数
```

---

### 我想要配置和优化

**数据库优化:**
```
工具: python backend/db_manager.py optimize
文档: DEPLOYMENT.md - "数据库优化" 部分
```

**API缓存:**
```
文件: backend/app.py
配置: Flask-Caching (需额外安装)
```

**性能监控:**
```
日志: backend 运行日志
监控: frontend 网络请求
```

---

### 我想要管理数据

**备份数据:**
```
命令: python backend/db_manager.py backup
```

**清理旧数据:**
```
命令: python backend/db_manager.py cleanup-data --days 365
```

**导出数据:**
```
命令: python backend/db_manager.py export comex_warehouse
```

**查看统计:**
```
命令: python backend/db_manager.py stats
```

---

## 📚 按学习路径查找

### 初学者路径

1. **安装和启动**
   - 文件: `QUICK_START.md`
   - 命令: `start.bat` / `start.sh`

2. **理解界面**
   - 文件: `frontend/index.html`
   - 导航: 5个标签页说明

3. **学习API**
   - 文件: `README.md` - "API接口" 部分
   - 测试: 使用 curl 或 Postman

4. **理解数据流**
   - 文件: `backend/data_collector.py`
   - 文件: `frontend/js/api.js`

### 中级开发者路径

1. **深入后端**
   - 文件: `backend/app.py`
   - 文件: `backend/models.py`
   - 文件: `backend/data_collector.py`

2. **前端开发**
   - 文件: `frontend/index.html`
   - 文件: `frontend/js/main.js`
   - 库: Chart.js 图表库

3. **数据库操作**
   - 文件: `backend/db_manager.py`
   - 工具: SQLite 管理

4. **部署和维护**
   - 文档: `DEPLOYMENT.md`
   - 脚本: 启动脚本

### 高级开发者路径

1. **扩展功能**
   - 添加新的采集器
   - 添加新的API端点
   - 优化性能

2. **生产部署**
   - Gunicorn + Nginx
   - Docker 容器化
   - 监控和日志

3. **高级特性**
   - 数据库分片
   - Redis缓存
   - 微服务架构

---

## 🔧 工具命令速查

### 启动命令
```powershell
# Windows
start.bat              # 启动后端
frontend-start.bat     # 启动前端

# Linux/Mac
./start.sh            # 启动所有
```

### 数据库命令
```bash
python backend/db_manager.py backup            # 备份
python backend/db_manager.py stats             # 统计
python backend/db_manager.py cleanup-logs      # 清理日志
python backend/db_manager.py cleanup-data      # 清理数据
python backend/db_manager.py optimize          # 优化
python backend/db_manager.py export <table>    # 导出
```

### 定时采集
```bash
python backend/scheduler.py
```

### 手动采集
```bash
python -c "from backend.data_collector import collect_all_data; collect_all_data()"
```

---

## 🐛 故障排查快速查找

| 问题 | 查看位置 |
|------|---------|
| CORS错误 | QUICK_START.md - 故障排查 |
| 端口被占用 | QUICK_START.md - 故障排查 |
| 连接失败 | DEPLOYMENT.md - 故障排查 |
| 数据库错误 | backend/db_manager.py |
| 图表不显示 | frontend/js/main.js |

---

## 📞 获取帮助

### 第1步: 查看文档
1. `QUICK_START.md` - 快速参考
2. `README.md` - 完整文档
3. `DEPLOYMENT.md` - 部署问题

### 第2步: 查看代码
1. 查看相关源文件的注释
2. 参考代码示例

### 第3步: 调试
1. 查看浏览器控制台错误
2. 查看服务器日志
3. 测试API端点

---

## 📊 项目概览

```
项目名称: 金银市场数据分析平台
版本: 1.0.0
发布日期: 2026年2月3日

核心指标:
├─ 文件总数: 20+
├─ 代码行数: ~3900
├─ 函数/方法: 50+
├─ API端点: 13个
├─ 数据表: 5个
└─ 文档页数: 6个

功能统计:
├─ 数据采集: 4类
├─ 前端标签: 5个
├─ 数据卡片: 15+
└─ 图表类型: 3个

技术栈:
├─ 后端: Python/Flask/SQLAlchemy
├─ 前端: HTML5/CSS3/JavaScript
├─ 图表: Chart.js
└─ 数据库: SQLite3
```

---

## ✨ 快速链接

### 常用文件
- 快速开始: `QUICK_START.md`
- 完整文档: `README.md`
- API参考: `README.md` - API部分
- 部署指南: `DEPLOYMENT.md`
- 项目总结: `PROJECT_SUMMARY.md`

### 核心代码
- API服务: `backend/app.py`
- 数据采集: `backend/data_collector.py`
- 前端主页: `frontend/index.html`
- 前端脚本: `frontend/js/main.js`

### 启动脚本
- 后端 (Win): `start.bat`
- 后端 (Linux/Mac): `start.sh`
- 前端: `frontend-start.bat`

---

## 📋 使用建议

1. **首次使用**: 阅读 `QUICK_START.md`
2. **深入学习**: 阅读 `README.md`
3. **部署上线**: 参考 `DEPLOYMENT.md`
4. **日常维护**: 使用 `db_manager.py`
5. **遇到问题**: 先查文档，再查代码

---

## 🎉 祝你使用愉快！

如有任何问题，请:
1. 查阅本索引找到相关文档
2. 阅读该文档的相关部分
3. 查看源代码的注释说明

**现在你已经准备好使用这个平台了！**

---

**最后更新**: 2026年2月3日  
**维护者**: AI开发助手
