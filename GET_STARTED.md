# 🚀 立即开始使用

## ⚡ 最快启动（仅需2步）

### 步骤1: 启动API服务器

```powershell
cd g:\Gold&Silver
.\quick-start.bat
```

**预期输出**:
```
============================================================
Silver & Gold Market Data API Server
============================================================
Server running on http://localhost:5000
API endpoints:
  GET  /api/health
  GET  /api/comex/latest
  ...
============================================================
```

### 步骤2: 在浏览器中测试

打开以下URL之一：

#### 选项A: 测试页面（推荐）
```
file:///g:/Gold&Silver/test.html
```
- 可视化界面
- 点击按钮即可测试
- 实时显示结果

#### 选项B: API直接访问
```
http://localhost:5000/api/health
```

#### 选项C: 查看API信息
```
http://localhost:5000/api
```

---

## 🌐 完整应用（5步启动）

### 步骤1: 启动API服务器

```powershell
cd g:\Gold&Silver
.\quick-start.bat
```

保持这个终端窗口打开！

### 步骤2: 打开新终端

按 `Windows + Shift + D` 打开新的终端窗口

### 步骤3: 启动前端服务器

```powershell
cd g:\Gold&Silver\frontend
python -m http.server 8000
```

### 步骤4: 在浏览器中访问

```
http://localhost:8000
```

### 步骤5: 享受应用！

现在你应该看到完整的金银市场分析平台界面

---

## 📱 三种使用方式

### 方式1: 仅API服务 (最小化)

```powershell
.\quick-start.bat
```

然后在任何HTTP客户端访问：
- `http://localhost:5000/api/health`
- `http://localhost:5000/api/comex/latest`
- `http://localhost:5000/api/etf/latest`

**用途**: API集成、测试、开发

### 方式2: API + 测试页面 (轻量级)

```powershell
.\quick-start.bat
```

然后打开：
```
file:///g:/Gold&Silver/test.html
```

**用途**: 快速测试、功能验证

### 方式3: API + 完整前端 (完整)

```powershell
# 终端1
.\quick-start.bat

# 终端2
cd frontend
python -m http.server 8000
```

访问: `http://localhost:8000`

**用途**: 完整应用、生产使用

---

## 🔍 验证服务器是否运行

### 使用浏览器
```
访问: http://localhost:5000/api/health
应该显示: JSON数据
```

### 使用PowerShell
```powershell
curl http://localhost:5000/api/health
# 或
Invoke-WebRequest http://localhost:5000/api/health
```

### 使用Python
```python
import urllib.request
response = urllib.request.urlopen('http://localhost:5000/api/health')
print(response.read().decode('utf-8'))
```

---

## 🛑 停止服务器

### 方式1: Ctrl+C
在运行脚本的终端中按 `Ctrl+C`

### 方式2: 关闭终端
直接关闭终端窗口

### 方式3: 使用任务管理器
1. 打开任务管理器 (Ctrl+Shift+Esc)
2. 找到 Python 进程
3. 右击 → 结束任务

---

## 📊 API端点速查

### 健康检查
```
GET http://localhost:5000/api/health
```

### COMEX数据
```
GET http://localhost:5000/api/comex/latest
```

### ETF数据
```
GET http://localhost:5000/api/etf/latest
```

### 市场价格
```
GET http://localhost:5000/api/price/latest
```

### 采集数据
```
POST http://localhost:5000/api/collect
```

---

## 🎯 常见任务

### 查看所有可用端点
访问: `http://localhost:5000/api`

### 测试API连接
访问: `http://localhost:5000/api/health`

### 获取COMEX库存
访问: `http://localhost:5000/api/comex/latest`

### 获取ETF持仓
访问: `http://localhost:5000/api/etf/latest`

### 获取市场价格
访问: `http://localhost:5000/api/price/latest`

### 手动采集数据
```powershell
Invoke-WebRequest -Method POST http://localhost:5000/api/collect
```

---

## 🐛 遇到问题？

### 问题: 无法启动脚本
**解决**:
```powershell
# 允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后运行脚本
.\quick-start.bat
```

### 问题: 端口被占用
```powershell
# 查找占用端口的进程
netstat -ano | findstr :5000

# 杀死进程
taskkill /PID <PID> /F
```

### 问题: 连接被拒绝
```powershell
# 检查防火墙
# 或者尝试访问: http://127.0.0.1:5000
```

### 问题: 看不到输出
```powershell
# 确保终端支持UTF-8
chcp 65001
```

---

## 📚 更多信息

### 快速参考
查看: `QUICK_START.md`

### 完整文档
查看: `README.md`

### 部署指南
查看: `DEPLOYMENT.md`

### 环境修复
查看: `ENVIRONMENT_FIX.md`

### 项目导航
查看: `INDEX.md`

---

## ✅ 检查清单

启动前确认:
- [ ] 已打开PowerShell或命令提示符
- [ ] 当前目录是 `g:\Gold&Silver`
- [ ] Python已安装（Python 3.7+）
- [ ] 没有其他应用占用端口5000和8000

---

## 🎉 完成！

现在你已经准备好使用金银市场数据分析平台了！

### 立即开始

```powershell
cd g:\Gold&Silver
.\quick-start.bat
```

有任何问题，查看相关文档或尝试我们提供的测试页面。

祝你使用愉快！🚀

---

**更新**: 2026年2月3日  
**版本**: 1.1 (修复版)
