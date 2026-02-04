import http.server
import socketserver
import os
import re
import urllib.request
import urllib.error
from datetime import datetime

# 强制禁用代理
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['no_proxy'] = '*'

PORT = 8000

# ==========================================
# 爬虫逻辑 (复用 SinaSpiderFetcher)
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
# Web Server Handler
# ==========================================
class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Fetch Data
            spider = SinaSpiderFetcher()
            codes = ['hf_SI', 'hf_GC', 'hf_HG', 'fx_sxagusd', 'fx_sxauusd', 'nf_AG0', 'fx_usdcny']
            data = spider.fetch_data(codes)
            
            # Helper to get formatted string
            def get_fmt(code, field='price', prefix='', suffix=''):
                val = data.get(code, {}).get(field, 'N/A')
                if val == 'N/A': return '<span class="loading">--</span>'
                if field == 'price':
                    return f"{prefix}{val}{suffix}"
                return f"{val}"
            
            def get_raw(code):
                return data.get(code, {}).get('price', 0)

            # Calculations
            ldn_silver = get_raw('fx_sxagusd')
            cmx_silver = get_raw('hf_SI')
            sh_silver = get_raw('nf_AG0')
            usdcny = get_raw('fx_usdcny')
            
            # EFP
            efp_silver = "N/A"
            if isinstance(ldn_silver, float) and isinstance(cmx_silver, float):
                efp_silver = f"${cmx_silver - ldn_silver:+.3f}"
            
            # Premium
            sh_premium = "N/A"
            if isinstance(sh_silver, float) and isinstance(usdcny, float) and isinstance(ldn_silver, float):
                try:
                    sh_usd = (sh_silver / usdcny) / 32.1507
                    prem = (sh_usd - ldn_silver) / ldn_silver * 100
                    sh_premium = f"{prem:+.2f}%"
                except: pass

            sys_time = datetime.now().strftime("%H:%M:%S")

            # HTML Template
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>金银市场数据分析平台</title>
                <meta http-equiv="refresh" content="1">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background-color: #f0f2f5; }}
                    .header {{ background-color: #003366; color: white; padding: 15px 30px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
                    .header h1 {{ margin: 0; font-size: 24px; display: flex; align-items: center; }}
                    .header .badge {{ background-color: #ff9800; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 10px; }}
                    .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }}
                    .card {{ background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }}
                    .card-header {{ padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; }}
                    .card-header h3 {{ margin: 0; color: #003366; font-size: 18px; display: flex; align-items: center; }}
                    .card-header .btn {{ background: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; }}
                    .card-body {{ padding: 20px; }}
                    
                    /* Table Styles */
                    .market-table {{ width: 100%; border-collapse: collapse; }}
                    .market-table th {{ text-align: left; color: #666; font-weight: normal; padding: 10px 0; border-bottom: 1px solid #eee; }}
                    .market-table td {{ padding: 12px 0; border-bottom: 1px solid #f9f9f9; font-size: 16px; font-weight: bold; color: #333; }}
                    .market-table .time {{ font-size: 12px; color: #999; font-weight: normal; margin-left: 10px; }}
                    .price-up {{ color: #d32f2f; }}
                    .price-down {{ color: #2e7d32; }}
                    .label {{ font-weight: normal; color: #555; }}
                    
                    /* Inventory Styles */
                    .inv-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }}
                    .inv-label {{ color: #555; }}
                    .inv-val {{ font-weight: bold; color: #003366; font-size: 18px; }}
                    
                    .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1><span class="badge">LIVE</span> 金银市场数据分析平台 (Global Precious Metals Monitor)</h1>
                    <div style="font-size: 14px;">System Time: {sys_time}</div>
                </div>

                <div class="container">
                    <!-- Left Column: Prices -->
                    <div class="card">
                        <div class="card-header">
                            <h3>📊 最新白银/黄金价格 (Latest Prices)</h3>
                            <button class="btn">数据加载成功</button>
                        </div>
                        <div class="card-body">
                            <table class="market-table">
                                <thead>
                                    <tr>
                                        <th>市场 (Market)</th>
                                        <th>现货/期货 (Price)</th>
                                        <th>更新时间 (Time)</th>
                                        <th>状态/价差 (Status)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="label">London Spot Silver</td>
                                        <td class="price-up">{get_fmt('fx_sxagusd', 'price', '$')}</td>
                                        <td>{get_fmt('fx_sxagusd', 'time')}</td>
                                        <td><span style="background:#fff3cd; padding:2px 5px; border-radius:3px; font-size:12px;">Base</span></td>
                                    </tr>
                                    <tr>
                                        <td class="label">COMEX Future Silver</td>
                                        <td class="price-up">{get_fmt('hf_SI', 'price', '$')}</td>
                                        <td>{get_fmt('hf_SI', 'time')}</td>
                                        <td>EFP: {efp_silver}</td>
                                    </tr>
                                    <tr>
                                        <td class="label">Shanghai Future Silver</td>
                                        <td class="price-up">{get_fmt('nf_AG0', 'price', '¥')}</td>
                                        <td>{get_fmt('nf_AG0', 'time')}</td>
                                        <td>Prem: {sh_premium}</td>
                                    </tr>
                                    <tr style="border-top: 2px solid #eee;">
                                        <td class="label">London Spot Gold</td>
                                        <td class="price-up">{get_fmt('fx_sxauusd', 'price', '$')}</td>
                                        <td>{get_fmt('fx_sxauusd', 'time')}</td>
                                        <td>--</td>
                                    </tr>
                                    <tr>
                                        <td class="label">COMEX Future Gold</td>
                                        <td class="price-up">{get_fmt('hf_GC', 'price', '$')}</td>
                                        <td>{get_fmt('hf_GC', 'time')}</td>
                                        <td>--</td>
                                    </tr>
                                    <tr>
                                        <td class="label">COMEX Copper</td>
                                        <td class="price-up">{get_fmt('hf_HG', 'price', '$')}</td>
                                        <td>{get_fmt('hf_HG', 'time')}</td>
                                        <td>--</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Right Column: Inventory -->
                    <div class="card">
                        <div class="card-header">
                            <h3>📦 COMEX库存 (Inventory)</h3>
                            <button class="btn">查看官方</button>
                        </div>
                        <div class="card-body">
                            <div class="inv-row">
                                <span class="inv-label">总库存 (Total)</span>
                                <span class="inv-val">442.48 Moz</span>
                            </div>
                            <div class="inv-row">
                                <span class="inv-label">合格 (Eligible)</span>
                                <span class="inv-val" style="color:#17a2b8;">317.04 Moz</span>
                            </div>
                            <div class="inv-row">
                                <span class="inv-label">注册 (Registered)</span>
                                <span class="inv-val" style="color:#28a745;">125.44 Moz</span>
                            </div>
                            <div class="inv-row" style="margin-top:20px; border:none;">
                                <span class="inv-label">更新时间</span>
                                <span style="color:#666;">2026/02/03</span>
                            </div>
                            <div style="margin-top: 20px; font-size: 12px; color: #888; background: #f8f9fa; padding: 10px; border-radius: 4px;">
                                <strong>提示:</strong> 库存数据基于交易所日报静态更新，非秒级跳动数据。
                            </div>
                        </div>
                    </div>
                </div>

                <div class="footer">
                    &copy; 2026 Global Precious Metals Monitor | Data Source: Sina Finance (Real-time)
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404)

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Serving Dashboard at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
