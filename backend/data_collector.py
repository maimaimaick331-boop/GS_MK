"""
数据采集模块 - 获取金银市场数据
"""
import requests
import json
import random
import time
import hashlib
import os
import io
import re
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging
from models import Session, ComexWarehouse, SilverETF, SilverPrice, GoldData, DataLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """数据采集器基类"""
    
    def __init__(self):
        self.session = Session()
        self.raw_data_base_path = Path("data/raw")
        self.raw_data_base_path.mkdir(parents=True, exist_ok=True)
    
    def save_raw_report(self, source: str, content: bytes, filename: str) -> str:
        """保存原始报表文件并返回 SHA256 哈希值"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_dir = self.raw_data_base_path / source / date_str
            save_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = save_dir / filename
            with open(file_path, "wb") as f:
                f.write(content)
            
            # 计算哈希
            file_hash = hashlib.sha256(content).hexdigest()
            logger.info(f"[{source}] Saved raw report: {file_path}, hash: {file_hash}")
            return file_hash
        except Exception as e:
            logger.error(f"[{source}] Failed to save raw report: {e}")
            return ""

    def log_data_collection(self, source: str, status: str, message: str = ""):
        """记录数据采集日志"""
        try:
            log = DataLog(source=source, status=status, message=message)
            self.session.add(log)
            self.session.commit()
            logger.info(f"[{source}] {status}: {message}")
        except Exception as e:
            logger.error(f"记录日志失败: {str(e)}")
            self.session.rollback()

class ComexDataCollector(DataCollector):
    """COMEX & LME 库存数据采集 - 增强审计链 (P0)"""

    def _fetch_quandl_silver(self) -> Optional[Dict[str, Any]]:
        try:
            url = "https://www.quandl.com/api/v3/datasets/CFTC/SI_FO_L_ALL"
            resp = requests.get(url, params={"api_key": "free", "rows": 1}, timeout=10)
            if resp.status_code != 200:
                return None
            payload = resp.json()
            dataset = payload.get("dataset", {})
            data = dataset.get("data", [])
            if not data:
                return None
            latest = data[0]
            date_str = latest[0]
            total = float(latest[1]) if len(latest) > 1 else None
            eligible = float(latest[2]) if len(latest) > 2 else None
            registered = float(latest[3]) if len(latest) > 3 else None
            return {
                "date": date_str,
                "total": total,
                "eligible": eligible,
                "registered": registered,
                "raw": latest,
                "source_url": url
            }
        except Exception as e:
            logger.error(f"[COMEX] Quandl fetch failed: {e}")
            return None

    def _parse_cme_report(self, content: bytes) -> Optional[Dict[str, Any]]:
        try:
            df = pd.read_excel(io.BytesIO(content), header=None)
            lower = df.astype(str).applymap(lambda x: x.strip().lower())
            header_row = None
            for i in range(len(lower)):
                row = lower.iloc[i].tolist()
                if any("eligible" in c for c in row) and any("registered" in c for c in row):
                    header_row = i
                    break
            if header_row is None or header_row + 1 >= len(df):
                return None
            header = lower.iloc[header_row].tolist()
            values = df.iloc[header_row + 1].tolist()
            total = eligible = registered = None
            for idx, cell in enumerate(header):
                if "total" in cell and total is None:
                    total = values[idx]
                elif "eligible" in cell and eligible is None:
                    eligible = values[idx]
                elif "registered" in cell and registered is None:
                    registered = values[idx]
            def to_number(val):
                if val is None:
                    return None
                if isinstance(val, (int, float)):
                    return float(val)
                s = str(val).replace(",", "").strip()
                return float(s) if s else None
            total = to_number(total)
            eligible = to_number(eligible)
            registered = to_number(registered)
            report_date = None
            date_pattern = re.compile(r"\d{4}[-/]\d{2}[-/]\d{2}")
            for row in lower.head(10).values.tolist():
                for cell in row:
                    m = date_pattern.search(cell)
                    if m:
                        report_date = m.group(0)
                        break
                if report_date:
                    break
            return {
                "total": total,
                "eligible": eligible,
                "registered": registered,
                "report_date": report_date,
                "header_row": header_row + 1
            }
        except Exception as e:
            logger.error(f"[COMEX] CME report parse failed: {e}")
            return None
    def collect_warehouse_data(self) -> Optional[List[Dict]]:
        """采集仓库库存数据 (COMEX/LME)"""
        try:
            results = []
            now = datetime.now(timezone.utc)
            as_of_date = now.strftime("%Y-%m-%d")

            cme_reports = {
                "silver": "https://www.cmegroup.com/delivery_reports/Silver_Stocks.xls",
                "gold": "https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls",
                "copper": "https://www.cmegroup.com/delivery_reports/Copper_Stocks.xls"
            }

            for metal, url in cme_reports.items():
                report_resp = requests.get(url, timeout=10)
                if report_resp.status_code == 200:
                    filename = url.split("/")[-1]
                    file_hash = self.save_raw_report("CME", report_resp.content, filename)
                    parsed = self._parse_cme_report(report_resp.content)
                else:
                    parsed = None
                    file_hash = ""

                if not parsed and metal == "silver":
                    qd = self._fetch_quandl_silver()
                    if qd:
                        parsed = {
                            "total": qd["total"],
                            "eligible": qd["eligible"],
                            "registered": qd["registered"],
                            "report_date": qd["date"],
                            "header_row": "quandl"
                        }
                        file_hash = ""

                if not parsed:
                    continue

                total = parsed["total"]
                eligible = parsed["eligible"]
                registered = parsed["registered"]

                if total is None or eligible is None or registered is None:
                    continue

                if metal in ["silver", "gold"] and total > 10000:
                    total = total / 1_000_000.0
                    eligible = eligible / 1_000_000.0
                    registered = registered / 1_000_000.0

                if metal == "copper" and total > 10000:
                    total = total / 2204.62
                    eligible = eligible / 2204.62
                    registered = registered / 2204.62

                diff = abs(total - (eligible + registered))
                quality = "REALTIME" if diff <= 0.01 else "ERROR_DIFF"

                data = {
                    "date": now,
                    "metal": metal,
                    "total_oz": total,
                    "eligible_oz": eligible,
                    "registered_oz": registered,
                    "price": 0.0,
                    "source": "CME",
                    "source_url": url,
                    "report_date": parsed.get("report_date") or as_of_date,
                    "fetched_at": now,
                    "field_name": "Total/Eligible/Registered",
                    "cell_ref": str(parsed.get("header_row")),
                    "file_hash": file_hash,
                    "quality": quality,
                    "raw_payload": json.dumps(parsed),
                    "mapping": f"Total({total}) = Eligible({eligible}) + Registered({registered})"
                }
                warehouse = ComexWarehouse(**data)
                self.session.add(warehouse)
                results.append(data)
                
            self.session.commit()
            self.log_data_collection('WAREHOUSE', 'success', f"Collected {len(results)} inventory items with audit chain")
            return results
        except Exception as e:
            self.log_data_collection('WAREHOUSE', 'fail', str(e))
            self.session.rollback()
            return None

class ETFDataCollector(DataCollector):
    """白银ETF数据采集 - 移除模拟随机数"""

    def _fetch_yahoo_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {"modules": "price,summaryDetail"}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            result = data.get("quoteSummary", {}).get("result", [])
            return result[0] if result else None
        except Exception as e:
            logger.error(f"[ETF] Yahoo fetch failed for {symbol}: {e}")
            return None

    def _fetch_metals_spot(self, metal: str) -> Optional[float]:
        try:
            url = f"https://api.metals.live/v1/spot/{metal}"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return None
            payload = resp.json()
            if isinstance(payload, list) and payload:
                item = payload[0]
                if isinstance(item, list) and len(item) >= 2:
                    return float(item[1])
                if isinstance(item, dict):
                    val = item.get(metal) or item.get("price")
                    return float(val) if val is not None else None
            if isinstance(payload, dict):
                val = payload.get("price") or payload.get(metal)
                return float(val) if val is not None else None
            return None
        except Exception as e:
            logger.error(f"[ETF] Metals.Live fetch failed: {e}")
            return None

    def collect_etf_data(self) -> Optional[List[Dict]]:
        """采集白银ETF持仓数据"""
        try:
            etf_list = [
                {"symbol": "SLV", "metal": "silver"},
                {"symbol": "PSLV", "metal": "silver"},
                {"symbol": "AGX", "metal": "silver"},
                {"symbol": "GLD", "metal": "gold"},
                {"symbol": "IAU", "metal": "gold"}
            ]

            results = []
            now = datetime.now(timezone.utc)
            spot_cache = {
                "silver": self._fetch_metals_spot("silver"),
                "gold": self._fetch_metals_spot("gold")
            }
            for etf in etf_list:
                quote = self._fetch_yahoo_quote(etf["symbol"])
                if not quote:
                    continue
                price = quote.get("price", {}).get("regularMarketPrice", {}).get("raw")
                change = quote.get("price", {}).get("regularMarketChange", {}).get("raw")
                total_assets = quote.get("summaryDetail", {}).get("totalAssets", {}).get("raw")
                holdings_oz = None
                metal_spot = spot_cache.get(etf["metal"])
                if total_assets and metal_spot:
                    holdings_oz = (float(total_assets) / float(metal_spot)) / 1_000_000.0
                etf_data = SilverETF(
                    date=now,
                    etf_name=etf["symbol"],
                    holdings_oz=holdings_oz,
                    yoy_change=None,
                    price=price or 0.0,
                    source="Yahoo Finance",
                    provider_as_of=quote.get("price", {}).get("regularMarketTime")
                )
                self.session.add(etf_data)
                results.append({
                    "etf_name": etf["symbol"],
                    "holdings_oz": holdings_oz,
                    "yoy_change": None,
                    "price": price,
                    "source": "Yahoo Finance"
                })
            
            self.session.commit()
            self.log_data_collection('ETF_DATA', 'success', f"Collected {len(results)} ETFs (Yahoo Finance)")
            return results
        except Exception as e:
            self.log_data_collection('ETF_DATA', 'fail', str(e))
            self.session.rollback()
            return None

class PriceDataCollector(DataCollector):
    """金银铜价格数据采集 - 接入真实 API (Sina & Yahoo)"""
    
    SINA_URL = "http://hq.sinajs.cn/list="
    YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
    
    # 映射表: 市场/品种 -> (Sina Symbol, Yahoo Symbol)
    SYMBOL_MAP = {
        "London_gold": ("hf_XAU", "XAUUSD=X"),
        "London_silver": ("hf_XAG", "XAGUSD=X"),
        "London_copper": ("hf_LMECA", "HG=F"), # LME 铜
        "Comex_gold": ("hf_GC", "GC=F"),
        "Comex_silver": ("hf_SI", "SI=F"),
        "Comex_copper": ("hf_HG", "HG=F"),
        "Shanghai_gold": ("nf_AU0", "AU=F"), # SHFE 黄金连续 (nf_前缀)
        "Shanghai_silver": ("nf_AG0", "SI=F"), # SHFE 白银连续
        "Shanghai_copper": ("nf_CU0", "HG=F")  # SHFE 铜连续
    }

    def _fetch_sina(self, symbols: List[str]) -> Dict[str, Any]:
        """从新浪财经获取真实数据"""
        try:
            url = f"{self.SINA_URL}{','.join(symbols)}"
            proxies = {"http": None, "https": None}
            headers = {"Referer": "http://finance.sina.com.cn"}
            resp = requests.get(url, headers=headers, timeout=5, proxies=proxies)
            content = resp.text
            
            results = {}
            for line in content.split('\n'):
                if not line or '=' not in line: continue
                symbol = line.split('var hq_str_')[1].split('=')[0]
                data_str = line.split('"')[1]
                if not data_str: continue
                fields = data_str.split(',')
                
                # 情况 1: 全球期货 hf_ 格式 (0:price, 6:time, 12:date)
                if symbol.startswith('hf_'):
                    if len(fields) >= 13:
                        results[symbol] = {
                            "last": float(fields[0]),
                            "time": f"{fields[12]} {fields[6]}",
                            "raw": fields
                        }
                # 情况 2: 国内期货 nf_ 格式 (nf_AU0, nf_AG0, nf_CU0)
                elif symbol.startswith('nf_'):
                    # 国内期货格式: 现价在 fields[8], 日期在 fields[1], 名字在 fields[0]
                    # 也有可能是: 名字, 时间, 开, 高, 低, 昨收, 持仓, 成交, 现价...
                    if len(fields) >= 9:
                        results[symbol] = {
                            "last": float(fields[8]),
                            "time": f"{datetime.now().strftime('%Y-%m-%d')} {fields[1]}",
                            "raw": fields
                        }
                # 情况 3: 旧版国内格式 (AU0, AG0)
                else:
                    if len(fields) >= 18:
                        results[symbol] = {
                            "last": float(fields[5]),
                            "time": f"{fields[17]} 00:00:00",
                            "raw": fields
                        }
            return results
        except Exception as e:
            logger.error(f"Sina API 抓取失败: {str(e)}")
            return {}

    def _fetch_yahoo(self, symbol: str) -> Dict[str, Any]:
        try:
            url = f"{self.YAHOO_URL}{symbol}"
            proxies = {"http": None, "https": None}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9"
            }
            for attempt in range(2):
                try:
                    resp = requests.get(url, headers=headers, timeout=5, proxies=proxies)
                    if resp.status_code == 200:
                        data = resp.json()
                        meta = data["chart"]["result"][0]["meta"]
                        price = meta.get("regularMarketPrice")
                        ts = meta.get("regularMarketTime")
                        logger.info(f"[Yahoo] Successfully fetched {symbol}: {price}")
                        return {"price": float(price), "time": ts, "raw": meta}
                    time.sleep(1)
                except Exception as ex:
                    logger.warning(f"[Yahoo] Attempt {attempt+1} failed for {symbol}: {ex}")
            return {}
        except Exception as e:
            logger.error(f"[Yahoo] Critical error fetching {symbol}: {e}")
            return {}

    def _fetch_metals_live(self, metal: str) -> Dict[str, Any]:
        try:
            url = f"https://api.metals.live/v1/spot/{metal}"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return {}
            payload = resp.json()
            if isinstance(payload, list) and payload:
                item = payload[0]
                if isinstance(item, list) and len(item) >= 2:
                    return {"price": float(item[1]), "time": item[0], "raw": item}
                if isinstance(item, dict):
                    val = item.get(metal) or item.get("price")
                    return {"price": float(val), "time": item.get("timestamp") or item.get("date"), "raw": item}
            if isinstance(payload, dict):
                val = payload.get("price") or payload.get(metal)
                return {"price": float(val), "time": payload.get("timestamp") or payload.get("date"), "raw": payload}
            return {}
        except Exception as e:
            logger.error(f"[Metals.Live] fetch failed for {metal}: {e}")
            return {}

    def _validate_data(self, main_val: float, backup_val: float, provider_as_of_str: str) -> Dict[str, Any]:
        """双源校验逻辑 (P0-4)"""
        try:
            provider_as_of = datetime.strptime(provider_as_of_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        except:
            provider_as_of = datetime.now(timezone.utc)
            
        now = datetime.now(timezone.utc)
        time_diff = (now - provider_as_of).total_seconds()
        
        is_error = 0
        quality = "REALTIME"
        
        # 1. |main - backup| / backup > 1% (如果备源有效)
        if backup_val > 0:
            diff_ratio = abs(main_val - backup_val) / backup_val
            if diff_ratio > 0.01:
                is_error = 1
                quality = "ERROR_DIFF"
        
        # 2. providerAsOf 过旧 (>1小时，考虑到非交易时间)
        if time_diff > 3600:
            is_error = 1
            quality = "DELAYED"
            
        return {"is_error": is_error, "quality": quality}

    def collect_prices_by_market(self, market: str) -> Optional[List[Dict]]:
        """按市场采集价格数据 (真实数据)"""
        try:
            results = []
            now = datetime.now(timezone.utc)
            metals = ["gold", "silver", "copper"]

            sina_symbols = [self.SYMBOL_MAP[f"{market}_{m}"][0] for m in metals]
            sina_data = self._fetch_sina(sina_symbols)

            for metal in metals:
                map_key = f"{market}_{metal}"
                sina_sym, yahoo_sym = self.SYMBOL_MAP[map_key]

                main_val = None
                as_of_str = ""
                raw_payload = {}
                source = ""

                if market == "London" and metal in ["gold", "silver"]:
                    api = self._fetch_metals_live(metal)
                    if api.get("price"):
                        main_val = api["price"]
                        as_of_str = str(api.get("time") or "")
                        raw_payload = api.get("raw") or {}
                        source = "Metals.Live"
                if main_val is None and market == "Comex":
                    api = self._fetch_yahoo(yahoo_sym)
                    if api.get("price"):
                        main_val = api["price"]
                        as_of_str = str(api.get("time") or "")
                        raw_payload = api.get("raw") or {}
                        source = "Yahoo"
                if main_val is None and sina_sym in sina_data:
                    main_val = sina_data[sina_sym]["last"]
                    as_of_str = sina_data[sina_sym]["time"]
                    raw_payload = sina_data[sina_sym]["raw"]
                    source = "Sina"
                if main_val is None:
                    api = self._fetch_yahoo(yahoo_sym)
                    if api.get("price"):
                        main_val = api["price"]
                        as_of_str = str(api.get("time") or "")
                        raw_payload = api.get("raw") or {}
                        source = "Yahoo"
                if main_val is None:
                    logger.error(f"[{market}] No real source for {metal}")
                    continue

                backup_val = None
                if source != "Sina" and sina_sym in sina_data:
                    backup_val = sina_data[sina_sym]["last"]
                if backup_val is None:
                    backup = self._fetch_yahoo(yahoo_sym)
                    if backup.get("price"):
                        backup_val = backup["price"]
                
                if map_key == "Comex_copper" and main_val > 100:
                    main_val = main_val / 100.0
                    logger.info(f"[Conversion] Comex Copper: {main_val*100} cents/lb -> {main_val} USD/lb")

                if map_key == "London_copper" and main_val < 50:
                    main_val = main_val * 2204.62
                    logger.info(f"[Conversion] London Copper: {main_val/2204.62} USD/lb -> {main_val} USD/ton")

                if backup_val is not None:
                    if map_key == "Comex_copper" and backup_val > 100:
                        backup_val = backup_val / 100.0
                    if map_key == "London_copper" and backup_val < 50:
                        backup_val = backup_val * 2204.62

                validation = self._validate_data(main_val, backup_val or main_val, as_of_str)
                
                spot_price = main_val
                futures_price = main_val
                if market == "Comex":
                    futures_price = main_val
                elif market == "London":
                    spot_price = main_val

                data = {
                    'date': now,
                    'market': market,
                    'metal': metal,
                    'spot_price': spot_price,
                    'futures_price': futures_price,
                    'premium': 0.0,
                    'premium_type': 'Premium',
                    'source': source,
                    'provider_as_of': as_of_str,
                    'field_used': 'last',
                    'quality': validation["quality"],
                    'raw_payload': json.dumps(raw_payload),
                    'mapping': json.dumps({"price": "api", "time": "provider"}),
                    'is_error': validation["is_error"]
                }

                price = SilverPrice(**data)
                self.session.add(price)
                results.append(data)
                
            self.session.commit()
            return results
        except Exception as e:
            logger.error(f"采集 {market} 价格失败: {str(e)}")
            self.session.rollback()
            return None

    def collect_london_price(self) -> Optional[List[Dict]]:
        return self.collect_prices_by_market("London")

    def collect_comex_price(self) -> Optional[List[Dict]]:
        return self.collect_prices_by_market("Comex")

    def collect_shanghai_price(self) -> Optional[List[Dict]]:
        return self.collect_prices_by_market("Shanghai")


class InvestmentAnalyticsCollector(DataCollector):
    """投资分析数据采集 - 移除模拟逻辑"""
    
    def collect_analytics_data(self) -> Optional[List[Dict]]:
        """采集分析数据 (当前使用静态基准，待接入专业报告解析)"""
        try:
            analytics = [
                # 认知层级
                {'category': '认知层级', 'indicator': '货币史视角', 'value': 8.5},
                {'category': '认知层级', 'indicator': '技术分析', 'value': 7.8},
                {'category': '认知层级', 'indicator': '全球化判断', 'value': 8.2},
                {'category': '认知层级', 'indicator': '货币势力预测', 'value': 7.5},
                
                # 逻辑层级
                {'category': '逻辑层级', 'indicator': '自由白银驱动', 'value': 9.1},
                {'category': '逻辑层级', 'indicator': '白银赤字', 'value': 8.7},
                {'category': '逻辑层级', 'indicator': '资源竞争', 'value': 8.9},
                {'category': '逻辑层级', 'indicator': '金融逻辑', 'value': 8.4},
            ]
            
            results = []
            now = datetime.now(timezone.utc)
            for item in analytics:
                data = GoldData(
                    date=now,
                    category=item['category'],
                    indicator=item['indicator'],
                    value=item['value']
                )
                self.session.add(data)
                results.append(item)
            
            self.session.commit()
            self.log_data_collection('ANALYTICS_DATA', 'success', "Analytics benchmarks loaded")
            return results
        except Exception as e:
            self.log_data_collection('ANALYTICS_DATA', 'fail', str(e))
            self.session.rollback()
            return None

def collect_all_data():
    """采集所有数据"""
    logger.info("=" * 50)
    logger.info("开始数据采集...")
    logger.info("=" * 50)
    
    # COMEX库存
    comex_collector = ComexDataCollector()
    comex_collector.collect_warehouse_data()
    
    # ETF数据
    etf_collector = ETFDataCollector()
    etf_collector.collect_etf_data()
    
    # 价格数据
    price_collector = PriceDataCollector()
    price_collector.collect_london_price()
    price_collector.collect_shanghai_price()
    price_collector.collect_comex_price()
    
    # 分析数据
    analytics_collector = InvestmentAnalyticsCollector()
    analytics_collector.collect_analytics_data()
    
    logger.info("=" * 50)
    logger.info("数据采集完成！")
    logger.info("=" * 50)

if __name__ == '__main__':
    from models import init_db
    init_db()
    collect_all_data()
