import http.server
import socketserver
import os
import re
import urllib.request
import urllib.error
import json
from datetime import datetime

# 强制禁用代理
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['no_proxy'] = '*'

PORT = 8000

# ==========================================
# 爬虫逻辑 (SinaSpiderFetcher)
# ==========================================
class SinaSpiderFetcher:
    def __init__(self):
        self.base_url = "http://hq.sinajs.cn/list={}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/"
        }

    def fetch_data(self, codes):
        url = self.base_url.format(",".join(codes))
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('gbk', errors='ignore')
                return self.parse_sina_response(content)
        except Exception as e:
            return {}

    def parse_sina_response(self, content):
        results = {}
        lines = content.strip().split('\n')
        for line in lines:
            match = re.match(r'var hq_str_(\w+)="(.*)";', line)
            if match:
                code = match.group(1)
                data_str = match.group(2)
                if not data_str: continue
                
                parts = data_str.split(',')
                price = "N/A"
                name = code
                update_time = "Wait..."
                
                if code.startswith('hf_'):
                    if len(parts) > 0: price = parts[0]
                    if len(parts) > 6: update_time = parts[6]
                    if len(parts) > 13: name = parts[13]
                elif code.startswith('fx_s') or code.startswith('fx_u'):
                    if len(parts) > 8:
                        update_time = parts[0]
                        price = parts[1]
                elif code.startswith('nf_'):
                    if len(parts) > 6: price = parts[6]
                    if len(parts) > 1:
                        t_str = parts[1]
                        if len(t_str) == 6: update_time = f"{t_str[:2]}:{t_str[2:4]}:{t_str[4:]}"
                        else: update_time = t_str

                try:
                    if price != "N/A": price = float(price)
                except: pass

                results[code] = {"price": price, "time": update_time, "name": name}
        return results

# ==========================================
# Web Server Handler (API + Static)
# ==========================================
class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # API Endpoint for JSON Data
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Fetch Live Data
            spider = SinaSpiderFetcher()
            # hf_SI: COMEX Silver Future, fx_sxagusd: London Silver Spot
            # nf_AG0: Shanghai Silver Future
            # hf_GC: COMEX Gold Future, fx_sxauusd: London Gold Spot
            # hf_HG: Copper
            codes = ['hf_SI', 'hf_GC', 'hf_HG', 'fx_sxagusd', 'fx_sxauusd', 'nf_AG0', 'fx_usdcny']
            raw_data = spider.fetch_data(codes)
            
            # Helper
            def get_val(code): return raw_data.get(code, {}).get('price', 0)
            def get_time(code): return raw_data.get(code, {}).get('time', '--')

            ldn_silver = get_val('fx_sxagusd')
            cmx_silver = get_val('hf_SI')
            sh_silver = get_val('nf_AG0')
            usdcny = get_val('fx_usdcny')
            
            # Calculations
            efp_silver = "N/A"
            if isinstance(ldn_silver, float) and isinstance(cmx_silver, float):
                efp_silver = f"${cmx_silver - ldn_silver:+.3f}"
            
            sh_premium = "N/A"
            status_sh = "Neutral"
            if isinstance(sh_silver, float) and isinstance(usdcny, float) and isinstance(ldn_silver, float):
                try:
                    sh_usd = (sh_silver / usdcny) / 32.1507
                    prem = (sh_usd - ldn_silver) / ldn_silver * 100
                    sh_premium = f"{prem:+.2f}%"
                    if prem > 10: status_sh = "High Demand"
                    elif prem < -1: status_sh = "Discount"
                    else: status_sh = "Normal"
                except: pass

            # Construct JSON Response
            response_data = {
                "sys_time": datetime.now().strftime("%H:%M:%S"),
                "prices": {
                    "ldn_silver_spot": {"price": ldn_silver, "time": get_time('fx_sxagusd')},
                    "ldn_gold_spot": {"price": get_val('fx_sxauusd'), "time": get_time('fx_sxauusd')},
                    
                    "cmx_silver_fut": {"price": cmx_silver, "time": get_time('hf_SI')},
                    "cmx_gold_fut": {"price": get_val('hf_GC'), "time": get_time('hf_GC')},
                    "cmx_copper": {"price": get_val('hf_HG'), "time": get_time('hf_HG')},
                    
                    "sh_silver_fut": {"price": sh_silver, "time": get_time('nf_AG0')},
                },
                "analysis": {
                    "efp_silver": efp_silver,
                    "sh_premium": sh_premium,
                    "status_sh": status_sh
                }
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return

        # Serve Main HTML
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>金银市场数据分析平台</title>
    <style>
        :root {
            --primary-blue: #0056b3;
            --header-bg: #004494;
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-dark: #333;
            --text-gray: #666;
            --up-color: #d93025; /* Red for up */
            --down-color: #188038; /* Green for down */
        }
        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; background-color: var(--bg-color); color: var(--text-dark); }
        
        /* Header */
        .header { background-color: var(--header-bg); color: white; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
        .header-logo { display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 600; }
        .header-logo span { background: #ff9800; padding: 2px 6px; border-radius: 4px; font-size: 12px; vertical-align: middle; }
        .header-status { font-size: 14px; opacity: 0.9; }

        /* Nav */
        .nav { background: #fff; border-bottom: 1px solid #ddd; padding: 0 40px; display: flex; gap: 30px; font-size: 14px; font-weight: 500; color: #555; }
        .nav-item { padding: 15px 0; border-bottom: 3px solid transparent; cursor: pointer; }
        .nav-item.active { border-bottom-color: var(--primary-blue); color: var(--primary-blue); }

        /* Main Content */
        .container { max-width: 1400px; margin: 25px auto; padding: 0 20px; display: grid; grid-template-columns: 3fr 2fr; gap: 25px; }

        /* Cards */
        .card { background: var(--card-bg); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }
        .card-header { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .card-title { font-size: 16px; font-weight: 700; color: var(--primary-blue); display: flex; align-items: center; gap: 8px; }
        .btn-refresh { background: #e8f0fe; color: var(--primary-blue); border: none; padding: 5px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; cursor: pointer; }

        /* Table Grid */
        .data-grid { display: grid; grid-template-columns: 1fr; }
        .data-row { display: grid; grid-template-columns: 2fr 1.5fr 1fr 1.5fr; padding: 15px 20px; border-bottom: 1px solid #f0f0f0; align-items: center; }
        .data-row:last-child { border-bottom: none; }
        .row-label { font-weight: 500; color: #444; }
        .row-price { font-weight: 700; font-size: 18px; color: var(--text-dark); text-align: right; font-family: Consolas, monospace; }
        .row-time { font-size: 12px; color: #999; text-align: right; padding-right: 15px; }
        .row-status { text-align: right; }
        .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .tag-green { background: #e6f4ea; color: #137333; }
        .tag-red { background: #fce8e6; color: #c5221f; }
        .tag-blue { background: #e8f0fe; color: #1967d2; }
        
        /* Inventory Specific */
        .inv-row { display: flex; justify-content: space-between; padding: 18px 20px; border-bottom: 1px solid #f5f5f5; align-items: center; }
        .inv-label { font-size: 14px; color: #555; font-weight: 500; }
        .inv-value { font-size: 20px; font-weight: 700; color: var(--primary-blue); }

        /* Animations */
        @keyframes flash-green { 0% { background-color: rgba(24, 128, 56, 0.2); } 100% { background-color: transparent; } }
        @keyframes flash-red { 0% { background-color: rgba(217, 48, 37, 0.2); } 100% { background-color: transparent; } }
        .flash-up { animation: flash-red 0.5s ease-out; } /* China: Red is Up */
        .flash-down { animation: flash-green 0.5s ease-out; } /* China: Green is Down */

    </style>
</head>
<body>

<div class="header">
    <div class="header-logo">
        <span>LIVE</span> 金银市场数据分析平台
    </div>
    <div class="header-status" id="sys-time">Connecting...</div>
</div>

<div class="nav">
    <div class="nav-item active">概览 Dashboard</div>
    <div class="nav-item">COMEX库存</div>
    <div class="nav-item">ETF持仓</div>
    <div class="nav-item">市场价格</div>
    <div class="nav-item">投资分析</div>
</div>

<div class="container">
    
    <!-- Left Column: Prices -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">📈 最新白银/黄金价格 (Live Prices)</div>
            <button class="btn-refresh">Auto-Refresh On</button>
        </div>
        <div class="data-grid">
            <!-- London Silver -->
            <div class="data-row" id="row-ldn-silver">
                <div class="row-label">London Spot Silver</div>
                <div class="row-price" id="p-ldn-silver">--</div>
                <div class="row-time" id="t-ldn-silver">--</div>
                <div class="row-status"><span class="tag tag-blue">Benchmark</span></div>
            </div>
            
            <!-- COMEX Silver -->
            <div class="data-row" id="row-cmx-silver">
                <div class="row-label">COMEX Silver Future</div>
                <div class="row-price" id="p-cmx-silver">--</div>
                <div class="row-time" id="t-cmx-silver">--</div>
                <div class="row-status" id="s-efp">--</div>
            </div>

            <!-- Shanghai Silver -->
            <div class="data-row" id="row-sh-silver">
                <div class="row-label">Shanghai Silver Fut</div>
                <div class="row-price" id="p-sh-silver">--</div>
                <div class="row-time" id="t-sh-silver">--</div>
                <div class="row-status" id="s-prem">--</div>
            </div>

            <!-- Separator -->
            <div style="height: 10px; background: #f9f9f9; border-top:1px solid #eee; border-bottom:1px solid #eee;"></div>

            <!-- London Gold -->
            <div class="data-row">
                <div class="row-label">London Spot Gold</div>
                <div class="row-price" id="p-ldn-gold">--</div>
                <div class="row-time" id="t-ldn-gold">--</div>
                <div class="row-status">--</div>
            </div>

            <!-- COMEX Gold -->
            <div class="data-row">
                <div class="row-label">COMEX Gold Future</div>
                <div class="row-price" id="p-cmx-gold">--</div>
                <div class="row-time" id="t-cmx-gold">--</div>
                <div class="row-status">--</div>
            </div>

             <!-- Copper -->
             <div class="data-row">
                <div class="row-label">COMEX Copper</div>
                <div class="row-price" id="p-cmx-copper">--</div>
                <div class="row-time" id="t-cmx-copper">--</div>
                <div class="row-status">--</div>
            </div>
        </div>
    </div>

    <!-- Right Column: Inventory -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">📦 COMEX库存 (Inventory)</div>
            <button class="btn-refresh">查看官方</button>
        </div>
        <div style="padding: 10px 0;">
            <div class="inv-row">
                <div class="inv-label">总库存 (Total Inventory)</div>
                <div class="inv-value">442.48 Moz</div>
            </div>
            <div class="inv-row">
                <div class="inv-label">合格 (Eligible)</div>
                <div class="inv-value" style="color: #1967d2;">317.04 Moz</div>
            </div>
            <div class="inv-row">
                <div class="inv-label">注册 (Registered)</div>
                <div class="inv-value" style="color: #188038;">125.44 Moz</div>
            </div>
            <div class="inv-row" style="background: #fafafa; border-bottom: none;">
                <div class="inv-label">更新时间 (Last Update)</div>
                <div style="font-size: 14px; color: #666;">2026/02/03 (User Report)</div>
            </div>
        </div>
        <div style="padding: 20px; color: #777; font-size: 13px; line-height: 1.5; border-top: 1px solid #eee;">
            <p><strong>注：</strong> 库存数据非秒级更新。以上数据基于用户提供的最新交易所日报截图录入。</p>
            <p><strong>Note:</strong> Inventory data is manually updated based on latest user report.</p>
        </div>
    </div>

</div>

<script>
    function updatePrice(id, val, prefix='') {
        const el = document.getElementById(id);
        if (!el) return;
        const oldVal = el.getAttribute('data-val');
        const newVal = val;
        
        if (newVal !== oldVal) {
            el.innerHTML = (val === 'N/A' || val === 0) ? '--' : prefix + val;
            el.setAttribute('data-val', newVal);
            // Flash effect
            if (oldVal && newVal > oldVal) {
                el.classList.remove('flash-down');
                el.classList.add('flash-up');
            } else if (oldVal && newVal < oldVal) {
                el.classList.remove('flash-up');
                el.classList.add('flash-down');
            }
            setTimeout(() => {
                el.classList.remove('flash-up', 'flash-down');
            }, 500);
        }
    }

    function updateText(id, val) {
        const el = document.getElementById(id);
        if(el) el.innerText = val;
    }

    function updateHTML(id, val) {
        const el = document.getElementById(id);
        if(el) el.innerHTML = val;
    }

    async function fetchData() {
        try {
            const res = await fetch('/api/data');
            const data = await res.json();
            
            // System Time
            updateText('sys-time', 'System Time: ' + data.sys_time);

            // Prices
            updatePrice('p-ldn-silver', data.prices.ldn_silver_spot.price, '$');
            updateText('t-ldn-silver', data.prices.ldn_silver_spot.time);

            updatePrice('p-cmx-silver', data.prices.cmx_silver_fut.price, '$');
            updateText('t-cmx-silver', data.prices.cmx_silver_fut.time);

            updatePrice('p-sh-silver', data.prices.sh_silver_fut.price, '¥');
            updateText('t-sh-silver', data.prices.sh_silver_fut.time);

            updatePrice('p-ldn-gold', data.prices.ldn_gold_spot.price, '$');
            updateText('t-ldn-gold', data.prices.ldn_gold_spot.time);

            updatePrice('p-cmx-gold', data.prices.cmx_gold_fut.price, '$');
            updateText('t-cmx-gold', data.prices.cmx_gold_fut.time);

            updatePrice('p-cmx-copper', data.prices.cmx_copper.price, '$');
            updateText('t-cmx-copper', data.prices.cmx_copper.time);

            // Analysis
            const efp = data.analysis.efp_silver;
            updateHTML('s-efp', `<span class="tag tag-blue">EFP: ${efp}</span>`);

            const prem = data.analysis.sh_premium;
            const status = data.analysis.status_sh;
            let color = 'tag-blue';
            if(status === 'High Demand') color = 'tag-red';
            if(status === 'Discount') color = 'tag-green';
            updateHTML('s-prem', `<span class="tag ${color}">Prem: ${prem}</span>`);

        } catch (e) {
            console.error(e);
        }
    }

    // Initial load
    fetchData();
    // Poll every 1s
    setInterval(fetchData, 1000);
</script>

</body>
</html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404)

if __name__ == '__main__':
    # Reuse address to avoid port in use errors
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Serving Dashboard v2 at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
