"""
轻量级Flask API替代品 - 使用Python标准库
集成真实API数据源 - 无需额外的pip依赖
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import sys
import logging
import threading
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'silver_gold.db')

# 导入真实API采集器
try:
    from real_api_collector import RealTimeDataCollector
    REAL_API_AVAILABLE = True
    logger.info("✓ Real API collector imported successfully")
except ImportError as e:
    REAL_API_AVAILABLE = False
    logger.warning(f"✗ Could not import real API collector: {e}")
    RealTimeDataCollector = None

# 全局数据缓存
data_cache = {
    'last_update': None,
    'silver_price': None,
    'gold_price': None,
    'etf_data': None,
    'comex_data': None,
    'economic_data': None
}

class DataHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        # CORS头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # 解析URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 路由处理
        if path == '/api/health':
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'Silver & Gold Market Data API'
            }
        
        elif path == '/api':
            response = {
                'service': 'Silver & Gold Market Data API',
                'version': '1.0.0',
                'endpoints': {
                    'health': '/api/health',
                    'comex': '/api/comex/latest',
                    'etf': '/api/etf/latest',
                    'prices': '/api/price/latest',
                    'collect': '/api/collect'
                }
            }
        
        elif path == '/api/comex/latest':
            response = self.get_comex_data()
        
        elif path == '/api/etf/latest':
            response = self.get_etf_data()
        
        elif path == '/api/price/latest':
            response = self.get_price_data()
        
        elif path == '/api/collect':
            response = self.collect_data()
        
        else:
            self.send_error(404, 'Not Found')
            return
        
        # 返回JSON
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """处理POST请求"""
        # CORS和响应头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 处理/api/collect POST请求
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/collect':
            response = self.collect_data()
        else:
            response = {'success': False, 'message': 'Not Found'}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_comex_data(self):
        """获取COMEX数据 - 使用真实API或缓存"""
        if REAL_API_AVAILABLE and data_cache['comex_data']:
            return {
                'success': True,
                'source': 'COMEX Official',
                'data': data_cache['comex_data'].get('warehouse_stocks', {})
            }
        
        # 备选数据
        return {
            'success': True,
            'source': 'COMEX',
            'data': {
                'date': datetime.now().isoformat(),
                'total_oz': 442.48,
                'eligible_oz': 317.04,
                'registered_oz': 125.44,
                'price': 31.50,
                'note': 'Using fallback data - API not available'
            }
        }
    
    def get_etf_data(self):
        """获取ETF数据 - 使用真实API或缓存"""
        if REAL_API_AVAILABLE and data_cache['etf_data']:
            return {
                'success': True,
                'source': 'Yahoo Finance',
                'data': data_cache['etf_data']
            }
        
        # 备选数据
        return {
            'success': True,
            'source': 'ETF Holdings',
            'data': [
                {'symbol': 'SLV', 'price': 31.50, 'change': 0.15, 'changePercent': 0.48, 'volume': 15000000},
                {'symbol': 'PSLV', 'price': 12.85, 'change': 0.10, 'changePercent': 0.78, 'volume': 5000000},
                {'symbol': 'AGX', 'price': 8.95, 'change': -0.05, 'changePercent': -0.56, 'volume': 2000000},
                {'symbol': 'GLD', 'price': 198.50, 'change': 0.50, 'changePercent': 0.25, 'volume': 12000000},
                {'symbol': 'IAU', 'price': 39.80, 'change': 0.10, 'changePercent': 0.25, 'volume': 8000000}
            ],
            'note': 'Using fallback data - API not available'
        }
    
    def get_price_data(self):
        """获取价格数据 - 使用真实API或缓存"""
        if REAL_API_AVAILABLE and data_cache['silver_price']:
            return {
                'success': True,
                'source': 'Metals.Live',
                'data': data_cache['silver_price']
            }
        
        # 备选数据
        return {
            'success': True,
            'source': 'Market Prices',
            'data': {
                'silver': {
                    'usd': 31.45,
                    'cny': 223.30,
                    'gbp': 24.85,
                    'source': 'Metals.Live'
                },
                'gold': {
                    'usd': 2050.00,
                    'cny': 14555.00,
                    'gbp': 1620.00,
                    'source': 'Metals.Live'
                },
                'markets': {
                    'London': {
                        'market': 'London',
                        'spot_price': 31.45,
                        'futures_price': 31.87,
                        'premium': 1.34,
                        'premium_type': 'Premium'
                    },
                    'Shanghai': {
                        'market': 'Shanghai',
                        'spot_price': 242.50,
                        'futures_price': 241.20,
                        'premium': -1.30,
                        'premium_type': 'Backwardation'
                    },
                    'Comex': {
                        'market': 'Comex',
                        'spot_price': 31.50,
                        'futures_price': 31.82,
                        'premium': 1.02,
                        'premium_type': 'Contango'
                    }
                }
            },
            'note': 'Using fallback data - API not available'
        }
    
    def collect_data(self):
        """采集数据 - 从真实API获取"""
        if REAL_API_AVAILABLE:
            try:
                logger.info("Starting real data collection...")
                collector = RealTimeDataCollector()
                result = collector.collect_all_market_data()
                
                # 更新缓存
                if result.get('data'):
                    data_cache['last_update'] = datetime.now().isoformat()
                    data_cache['silver_price'] = result['data'].get('silver_price')
                    data_cache['gold_price'] = result['data'].get('gold_price')
                    data_cache['etf_data'] = result['data'].get('etf_holdings')
                    data_cache['comex_data'] = result['data'].get('comex_stocks')
                    data_cache['economic_data'] = result['data'].get('economic_indicators')
                
                return {
                    'success': True,
                    'message': 'Data collection from real APIs completed',
                    'timestamp': datetime.now().isoformat(),
                    'data_sources': [
                        'Metals.Live (Silver & Gold Prices)',
                        'Yahoo Finance (ETF Data)',
                        'COMEX/Quandl (Warehouse Stocks)',
                        'World Bank (Economic Indicators)'
                    ]
                }
            except Exception as e:
                logger.error(f"Real data collection error: {e}")
                return {
                    'success': False,
                    'message': f'Data collection failed: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
        
        return {
            'success': True,
            'message': 'Data collection completed (using fallback data)',
            'timestamp': datetime.now().isoformat(),
            'note': 'Real API collector not available'
        }
    
    def log_message(self, format, *args):
        """禁用默认日志"""
        pass


def init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comex_warehouse (
                id INTEGER PRIMARY KEY,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_oz REAL,
                eligible_oz REAL,
                registered_oz REAL,
                price REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS silver_etf (
                id INTEGER PRIMARY KEY,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                etf_name TEXT,
                holdings_oz REAL,
                yoy_change REAL,
                price REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS silver_price (
                id INTEGER PRIMARY KEY,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                market TEXT,
                spot_price REAL,
                futures_price REAL,
                premium REAL,
                premium_type TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print('Database initialized successfully')


def main():
    """启动服务器"""
    init_db()
    
    # 后台任务：定期采集真实数据
    if REAL_API_AVAILABLE:
        def background_data_collection():
            """后台采集数据"""
            logger.info("Background data collection thread started")
            collector = RealTimeDataCollector()
            while True:
                try:
                    time.sleep(3600)  # 每小时采集一次
                    logger.info("Running scheduled data collection...")
                    result = collector.collect_all_market_data()
                    
                    if result.get('data'):
                        data_cache['last_update'] = datetime.now().isoformat()
                        data_cache['silver_price'] = result['data'].get('silver_price')
                        data_cache['gold_price'] = result['data'].get('gold_price')
                        data_cache['etf_data'] = result['data'].get('etf_holdings')
                        data_cache['comex_data'] = result['data'].get('comex_stocks')
                        data_cache['economic_data'] = result['data'].get('economic_indicators')
                except Exception as e:
                    logger.error(f"Background collection error: {e}")
        
        # 启动后台线程
        bg_thread = threading.Thread(target=background_data_collection, daemon=True)
        bg_thread.start()
        logger.info("✓ Background data collection thread started")
    
    server = HTTPServer(('localhost', 5000), DataHandler)
    print('='*60)
    print('Silver & Gold Market Data API Server')
    print('='*60)
    print('Server running on http://localhost:5000')
    print('API endpoints:')
    print('  GET  /api/health')
    print('  GET  /api/comex/latest')
    print('  GET  /api/etf/latest')
    print('  GET  /api/price/latest')
    print('  POST /api/collect')
    print('')
    if REAL_API_AVAILABLE:
        print('✓ Real API data collection enabled')
    else:
        print('⚠ Real API data collection disabled - using fallback data')
    print('='*60)
    print('Press Ctrl+C to stop')
    print('='*60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped')
        server.shutdown()


if __name__ == '__main__':
    main()
