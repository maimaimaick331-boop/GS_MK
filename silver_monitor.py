import os
import time
import sys
import re
import urllib.request
import urllib.error
from datetime import datetime

# 强制禁用代理，防止 WinError 10061
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['no_proxy'] = '*'

# ==========================================
# 配置区域 / CONFIGURATION
# ==========================================
# 刷新频率 (秒)
REFRESH_RATE = 1

# ==========================================
# 爬虫类 / SPIDERS
# ==========================================

class SinaSpiderFetcher:
    def __init__(self):
        self.base_url = "http://hq.sinajs.cn/list={}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/"
        }

    def fetch_data(self, codes):
        """
        批量获取数据
        codes: list of strings
        Returns: dict {code: (price, name, time, open_interest)}
        """
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
                if not data_str:
                    continue
                
                parts = data_str.split(',')
                price = "N/A"
                name = code
                update_time = "Wait..."
                open_interest = "N/A"

                # 1. 国际期货 (hf_SI, hf_GC, hf_HG)
                # Raw: 87.670,,87.590,87.650,87.850,79.010,21:06:31,...
                if code.startswith('hf_'):
                    if len(parts) > 0:
                        price = parts[0]  # Current Price
                    if len(parts) > 6:
                        update_time = parts[6] # Time
                    if len(parts) > 13:
                        name = parts[13] # Name

                # 2. 外汇/现货 (fx_sxagusd, fx_usdcny)
                # Raw fx_s: 21:04:02,87.659...,87.598...,...
                elif code.startswith('fx_s') or code.startswith('fx_u'):
                    if len(parts) > 8:
                        update_time = parts[0] # Time at Index 0 for FX
                        price = parts[1]       # Price at Index 1 for FX
                        
                        if "ag" in code: name = "伦敦白银"
                        if "au" in code: name = "伦敦黄金"
                        if "cny" in code: name = "美元人民币"

                # 3. 国内期货 (nf_AG0)
                # Raw: 白银连续,210631,22000.000,22446.000,21919.000,0.000,22405.000...
                elif code.startswith('nf_'):
                    if len(parts) > 6:
                        price = parts[6] # Last Price
                    if len(parts) > 1:
                        # Time is hhmmss
                        t_str = parts[1]
                        if len(t_str) == 6:
                            update_time = f"{t_str[:2]}:{t_str[2:4]}:{t_str[4:]}"
                        else:
                            update_time = t_str
                    if len(parts) > 0:
                        name = parts[0]

                # Format Price
                try:
                    if price != "N/A":
                        price = float(price)
                except:
                    pass

                results[code] = {
                    "price": price,
                    "name": name,
                    "time": update_time,
                    "open_interest": open_interest
                }
        return results

# ==========================================
# 主程序 / MAIN
# ==========================================

def main():
    print("=== 启动实时行情监控 (Sina 直连版) ===")
    
    spider = SinaSpiderFetcher()
    target_codes = ['hf_SI', 'hf_GC', 'hf_HG', 'fx_sxagusd', 'fx_sxauusd', 'nf_AG0', 'fx_usdcny'] 

    # 静态库存数据 (来源: 用户提供 2026/02/03 截图)
    # COMEX Inventory
    inv_comex_total = "442.48 Moz"
    inv_comex_elig = "317.04 Moz"
    inv_comex_reg = "125.44 Moz"
    inv_update_time = "2026/02/03"

    try:
        while True:
            data_map = spider.fetch_data(target_codes)
            sys_time = datetime.now().strftime("%H:%M:%S")
            
            # --- Helper ---
            def get_val(code, field='price'):
                return data_map.get(code, {}).get(field, 'N/A')

            # Prices
            london_gold = get_val('fx_sxauusd')
            comex_gold = get_val('hf_GC')
            
            london_silver = get_val('fx_sxagusd')
            comex_silver = get_val('hf_SI')
            shanghai_silver = get_val('nf_AG0') # RMB/kg
            
            comex_copper = get_val('hf_HG')
            usdcny = get_val('fx_usdcny')

            # Timestamps
            time_ldn = get_val('fx_sxagusd', 'time')
            time_ny = get_val('hf_SI', 'time')
            time_sh = get_val('nf_AG0', 'time')

            # --- 计算指标 ---
            # 1. EFP (纽约 - 伦敦)
            efp_silver = "N/A"
            if isinstance(comex_silver, float) and isinstance(london_silver, float):
                efp_val = comex_silver - london_silver
                efp_silver = f"${efp_val:+.3f}"
            
            # 2. 上海溢价 (Shanghai Premium)
            sh_premium = "N/A"
            sh_usd_price = 0
            if isinstance(shanghai_silver, float) and isinstance(usdcny, float) and isinstance(london_silver, float):
                try:
                    # 1 kg = 32.1507 troy oz
                    # RMB/kg -> USD/oz: (Price / USDCNY) / 32.1507
                    # 修正: (22405 / 7.25) / 32.1507 = 96.1 USD/oz
                    sh_usd_price = (shanghai_silver / usdcny) / 32.1507
                    prem_val = (sh_usd_price - london_silver) / london_silver * 100
                    sh_premium = f"{prem_val:+.2f}% (${sh_usd_price:.2f})"
                except:
                    pass

            # -------------------------------------------------
            # 界面绘制 / UI RENDERING
            # -------------------------------------------------
            os.system('cls' if os.name == 'nt' else 'clear')

            print("=" * 90)
            print(f"{'全球贵金属实时监控 / GLOBAL PRECIOUS METALS MONITOR':^90}")
            print("=" * 90)
            print(f" System Time: {sys_time} | Refresh: {REFRESH_RATE}s | USD/CNY: {usdcny} | Src: Sina Finance (Live)")
            print("-" * 90)

            # 表头
            print(f"| {'指标 (Indicator)':<16} | {'伦敦 (London Spot)':<22} | {'纽约 (COMEX Fut)':<22} | {'上海 (SHFE)':<22} |")
            print("-" * 90)

            # 黄金
            print(f"| {'黄金 (Gold)':<16} | ${str(london_gold):<12}           | ${str(comex_gold):<12}           | {'--':<22} |")
            
            # 白银 (带时间戳)
            print(f"| {'白银 (Silver)':<16} | ${str(london_silver):<12} {time_ldn:<8} | ${str(comex_silver):<12} {time_ny:<8} | ¥{str(shanghai_silver):<10} {time_sh:<8} |")
            
            # 铜
            print(f"| {'铜 (Copper)':<16} | {'--':<22} | ${str(comex_copper):<22} | {'--':<22} |")

            print("-" * 90)
            # 套利分析
            print(f"| {'价差分析':<16} | {'EFP (NY-LDN)':<22} | {'SH Premium':<47} |")
            print(f"| {'Spread':<16} | {efp_silver:<22} | {sh_premium:<47} |")
            
            print("-" * 90)
            # 库存信息
            print(f"| {'库存 (Inventory)':<16} | {'COMEX Total':<22} | {'Eligible':<22} | {'Registered':<22} |")
            print(f"| {'白银 (Silver)':<16} | {inv_comex_total:<22} | {inv_comex_elig:<22} | {inv_comex_reg:<22} |")
            print(f"| {'更新时间':<16} | {inv_update_time:<22} | {'(Source: User Data)':<47} |")
            
            print("=" * 90)
            print(" [Note] Inventory data is static from user provided screenshot.")
            print(" [Note] Prices are live from Sina Finance (2026 Market Data).")
            print(" [Note] If prices differ from expectations, check contract validity or data source delays.")

            time.sleep(REFRESH_RATE)

    except KeyboardInterrupt:
        print("\n监控已停止。")
    except Exception as e:
        print(f"\n发生未知错误: {e}")

if __name__ == "__main__":
    main()