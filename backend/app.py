"""
Flask API服务器
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from models import Session, ComexWarehouse, SilverETF, SilverPrice, GoldData, DataLog, init_db
from data_collector import collect_all_data
import logging
import json
import threading
import time

# ==================== 后台任务 ====================

def background_collector():
    """后台循环采集数据，模拟实时更新"""
    logger.info("启动后台数据采集线程...")
    while True:
        try:
            collect_all_data()
            time.sleep(2)  # 每2秒采集一次
        except Exception as e:
            logger.error(f"后台采集异常: {e}")
            time.sleep(5)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 在应用启动时开启线程
collector_thread = threading.Thread(target=background_collector, daemon=True)
collector_thread.start()

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """后端状态页，引导至前端"""
    return """
    <h1>金银市场数据分析平台 - API 服务已启动</h1>
    <p>当前处于后端 API 模式。请访问前端 UI 界面：</p>
    <a href="http://localhost:8000" style="font-size: 20px; color: blue;">点击进入终端 UI (http://localhost:8000)</a>
    <hr>
    <h3>可用 API 端点:</h3>
    <ul>
        <li><a href="/api/price/latest">/api/price/latest</a> - 最新市场价格</li>
        <li><a href="/api/comex/latest">/api/comex/latest</a> - COMEX 综合数据</li>
    </ul>
    """

# 初始化数据库
init_db()

# ==================== 辅助函数 ====================

def serialize_datetime(obj):
    """序列化datetime对象"""
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError(f"Type {type(obj)} not serializable")

def query_to_dict(model_instance):
    """将SQLAlchemy对象转换为字典"""
    if model_instance is None:
        return None
    return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

# ==================== 数据采集路由 ====================

@app.route('/api/collect', methods=['POST'])
def trigger_collection():
    """手动触发数据采集"""
    try:
        collect_all_data()
        return jsonify({
            'success': True,
            'message': '数据采集成功',
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        logger.error(f"数据采集失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==================== COMEX数据路由 ====================

@app.route('/api/comex/warehouse', methods=['GET'])
def get_warehouse_data():
    """获取COMEX仓库库存数据"""
    try:
        session = Session()
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        data = session.query(ComexWarehouse).filter(
            ComexWarehouse.date >= start_date
        ).order_by(ComexWarehouse.date.desc()).all()
        
        result = [query_to_dict(item) for item in data]
        session.close()
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/comex/latest', methods=['GET'])
def get_warehouse_latest():
    """获取最新库存数据 (COMEX & LME)"""
    try:
        session = Session()
        
        # 定义需要获取的数据源和金属
        sources = {
            'CME': ['silver', 'gold', 'copper'],
            'LME': ['silver', 'copper']
        }
        
        result = {
            'comex': {},
            'lme': {}
        }
        
        for source, metals in sources.items():
            target_key = 'comex' if source == 'CME' else 'lme'
            for metal in metals:
                data = session.query(ComexWarehouse).filter(
                    ComexWarehouse.source == source,
                    ComexWarehouse.metal == metal
                ).order_by(ComexWarehouse.date.desc()).first()
                
                if data:
                    result[target_key][metal] = query_to_dict(data)
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/inventory/aggregated', methods=['GET'])
def get_inventory_aggregated():
    """聚合三地库存数据 (COMEX, LME, SHFE)"""
    try:
        session = Session()
        
        # 1. 获取 COMEX (CME) 最新数据
        comex_data = {}
        for metal in ['silver', 'gold', 'copper']:
            data = session.query(ComexWarehouse).filter(
                ComexWarehouse.source == 'CME',
                ComexWarehouse.metal == metal
            ).order_by(ComexWarehouse.date.desc()).first()
            if data:
                comex_data[metal] = query_to_dict(data)
        
        # 2. 获取 LME 最新数据
        lme_data = {}
        for metal in ['silver', 'copper']:
            data = session.query(ComexWarehouse).filter(
                ComexWarehouse.source == 'LME',
                ComexWarehouse.metal == metal
            ).order_by(ComexWarehouse.date.desc()).first()
            if data:
                lme_data[metal] = query_to_dict(data)
        
        # 3. 获取 SHFE 最新数据 (如果数据库没有，则返回模拟数据以保证 UI 完整)
        shfe_data = {}
        for metal in ['silver', 'gold', 'copper']:
            data = session.query(ComexWarehouse).filter(
                ComexWarehouse.source == 'SHFE',
                ComexWarehouse.metal == metal
            ).order_by(ComexWarehouse.date.desc()).first()
            if data:
                shfe_data[metal] = query_to_dict(data)
            else:
                # 模拟数据 (单位: 吨)
                mocks = {
                    'silver': {'total_oz': 1250.5, 'eligible_oz': 800.0, 'registered_oz': 450.5, 'unit': '吨'},
                    'gold': {'total_oz': 5.2, 'eligible_oz': 3.0, 'registered_oz': 2.2, 'unit': '吨'},
                    'copper': {'total_oz': 85000, 'eligible_oz': 50000, 'registered_oz': 35000, 'unit': '吨'}
                }
                shfe_data[metal] = {
                    'metal': metal,
                    'total_oz': mocks[metal]['total_oz'],
                    'eligible_oz': mocks[metal]['eligible_oz'],
                    'registered_oz': mocks[metal]['registered_oz'],
                    'source': 'SHFE',
                    'quality': 'MOCKED',
                    'report_date': datetime.now().strftime('%Y-%m-%d'),
                    'unit': mocks[metal].get('unit', '吨')
                }

        session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'comex': comex_data,
                'lme': lme_data,
                'shfe': shfe_data,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        logger.error(f"聚合库存查询失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ETF数据路由 ====================

@app.route('/api/etf/holdings', methods=['GET'])
def get_etf_data():
    """获取ETF持仓数据"""
    try:
        session = Session()
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        data = session.query(SilverETF).filter(
            SilverETF.date >= start_date
        ).order_by(SilverETF.date.desc()).all()
        
        result = [query_to_dict(item) for item in data]
        session.close()
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/etf/latest', methods=['GET'])
def get_etf_latest():
    """获取最新ETF数据"""
    try:
        session = Session()
        data = session.query(SilverETF).order_by(
            SilverETF.date.desc()
        ).all()
        
        # 按ETF名称分组
        etf_dict = {}
        for item in data:
            if item.etf_name not in etf_dict:
                etf_dict[item.etf_name] = query_to_dict(item)
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': list(etf_dict.values())
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 价格数据路由 ====================

@app.route('/api/price/all', methods=['GET'])
def get_all_prices():
    """获取所有市场价格"""
    try:
        session = Session()
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        data = session.query(SilverPrice).filter(
            SilverPrice.date >= start_date
        ).order_by(SilverPrice.date.desc()).all()
        
        result = [query_to_dict(item) for item in data]
        session.close()
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/price/latest', methods=['GET'])
def get_latest_prices():
    """获取最新价格（各市场各金属最新数据）"""
    try:
        session = Session()
        markets = ['London', 'Shanghai', 'Comex']
        metals = ['silver', 'gold', 'copper']
        
        result = {}
        for market in markets:
            market_data = {}
            for metal in metals:
                data = session.query(SilverPrice).filter(
                    SilverPrice.market == market,
                    SilverPrice.metal == metal
                ).order_by(SilverPrice.date.desc()).first()
                
                if data:
                    market_data[metal] = query_to_dict(data)
                    # 兼容前端字段名 price
                    market_data[metal]['price'] = market_data[metal].get('spot_price') or market_data[metal].get('futures_price') or 0.0
            
            logger.info(f"Market {market} data keys: {list(market_data.keys())}")
            if market_data:
                result[market] = market_data
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/price/by-market/<market>', methods=['GET'])
def get_market_prices(market):
    """获取特定市场的价格数据"""
    try:
        session = Session()
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        data = session.query(SilverPrice).filter(
            SilverPrice.market == market,
            SilverPrice.date >= start_date
        ).order_by(SilverPrice.date.desc()).all()
        
        result = [query_to_dict(item) for item in data]
        session.close()
        
        return jsonify({
            'success': True,
            'market': market,
            'count': len(result),
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 分析数据路由 ====================

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """获取投资分析数据"""
    try:
        session = Session()
        category = request.args.get('category')
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = session.query(GoldData).filter(
            GoldData.date >= start_date
        )
        
        if category:
            query = query.filter(GoldData.category == category)
        
        data = query.order_by(GoldData.date.desc()).all()
        
        result = [query_to_dict(item) for item in data]
        session.close()
        
        return jsonify({
            'success': True,
            'count': len(result),
            'category': category,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """获取分析摘要"""
    try:
        session = Session()
        categories = ['认知层级', '逻辑层级', '数据层级', '风险层级']
        
        result = {}
        for category in categories:
            data = session.query(GoldData).filter(
                GoldData.category == category
            ).order_by(GoldData.date.desc()).all()
            
            if data:
                result[category] = [query_to_dict(item) for item in data[:4]]
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 日志路由 ====================

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取数据采集日志"""
    try:
        session = Session()
        limit = request.args.get('limit', 50, type=int)
        
        data = session.query(DataLog).order_by(
            DataLog.created_at.desc()
        ).limit(limit).all()
        
        result = [query_to_dict(item) for item in data]
        session.close()
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 调试元信息路由 ====================

@app.route('/api/debug/raw', methods=['GET'])
def get_debug_raw():
    """获取特定 key 的原始调试元信息 (P0-2)"""
    try:
        key = request.args.get('key')
        if not key:
            return jsonify({'success': False, 'message': 'Missing key parameter'}), 400
        
        session = Session()
        
        # 尝试从价格表中查找 (metal 为 key)
        price_data = session.query(SilverPrice).filter(
            SilverPrice.metal.ilike(key)
        ).order_by(SilverPrice.date.desc()).first()
        
        # 如果没找到，尝试从库存表中查找
        warehouse_data = None
        if not price_data:
            warehouse_data = session.query(ComexWarehouse).filter(
                ComexWarehouse.metal.ilike(key)
            ).order_by(ComexWarehouse.date.desc()).first()
            
        data = price_data or warehouse_data
        
        if not data:
            session.close()
            return jsonify({'success': False, 'message': f'No data found for key: {key}'}), 404
            
        result = {
            'key': key,
            'raw_payload': json.loads(data.raw_payload) if data.raw_payload else {},
            'mapping': json.loads(data.mapping) if data.mapping else {},
            'source': data.source,
            'provider_as_of': data.provider_as_of,
            'field_used': data.field_used,
            'quality': data.quality,
            'is_error': data.is_error,
            'timestamp': data.date.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        session.close()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"获取调试信息失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 健康检查 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'service': 'Silver & Gold Market Data API'
    })

@app.route('/api', methods=['GET'])
def api_info():
    """API信息"""
    return jsonify({
        'service': 'Silver & Gold Market Data API',
        'version': '1.0.0',
        'description': '金银市场数据采集和分析API',
        'endpoints': {
            'collection': '/api/collect',
            'comex': '/api/comex/warehouse',
            'etf': '/api/etf/holdings',
            'prices': '/api/price/all',
            'analytics': '/api/analytics',
            'logs': '/api/logs'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
