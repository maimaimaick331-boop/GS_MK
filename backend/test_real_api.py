#!/usr/bin/env python3
"""
测试真实API数据采集
验证所有数据源是否可用
"""

import sys
import os

# 添加backend路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from real_api_collector import RealTimeDataCollector
import json
from datetime import datetime

def test_complete_collection():
    """测试完整数据采集"""
    print("\n" + "="*60)
    print("完整数据采集测试")
    print("="*60)
    
    collector = RealTimeDataCollector()
    print("\n开始采集所有市场数据...")
    
    data = collector.collect_all_market_data()
    
    print("\n" + "="*60)
    print("采集结果摘要")
    print("="*60)
    
    if data.get('data'):
        print("\n已成功采集的数据类型:")
        
        if 'silver_price' in data['data'] and data['data']['silver_price']:
            sp = data['data']['silver_price']
            print(f"  ✓ 白银价格: ${sp['silver']['usd']}/oz (CNY: ¥{sp['silver']['cny']})")
        
        if 'gold_price' in data['data'] and data['data']['gold_price']:
            gp = data['data']['gold_price']
            print(f"  ✓ 黄金价格: ${gp['gold']['usd']}/oz (CNY: ¥{gp['gold']['cny']})")
        
        if 'etf_holdings' in data['data'] and data['data']['etf_holdings']:
            etfs = data['data']['etf_holdings']
            print(f"  ✓ ETF数据 ({len(etfs)} 个):")
            for etf in etfs:
                print(f"     - {etf['symbol']}: ${etf['price']}")
        
        if 'comex_stocks' in data['data'] and data['data']['comex_stocks']:
            cs = data['data']['comex_stocks']
            stocks = cs.get('warehouse_stocks', {})
            print(f"  ✓ COMEX库存: {stocks.get('total_oz')}M oz")
        
        if 'market_prices' in data['data'] and data['data']['market_prices']:
            print("  ✓ 市场价格数据:")
            for market, prices in data['data']['market_prices'].get('markets', {}).items():
                print(f"     - {market}: ${prices['spot_price']}")
        
        if 'economic_indicators' in data['data'] and data['data']['economic_indicators']:
            ei = data['data']['economic_indicators']
            indicators = ei.get('indicators', {})
            print(f"  ✓ 经济指标: 美国通胀率 {indicators.get('inflation_rate_us', {}).get('value')}%")
        
        # 保存完整数据到文件
        output_file = os.path.join(os.path.dirname(__file__), 'test_api_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 完整结果已保存到: {output_file}")
    else:
        print("✗ 数据采集失败")
    
    return data


if __name__ == '__main__':
    print("\n")
    print("█"*60)
    print("█  金银市场数据实时API测试")
    print("█"*60)
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("█"*60)
    
    # 运行完整测试
    complete_data = test_complete_collection()
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)
    print("\n数据源说明:")
    if complete_data.get('data_sources'):
        for key, source in complete_data['data_sources'].items():
            print(f"  • {key}: {source}")
    
    print("\n提示:")
    print("  • 所有数据均从真实API源获取或使用官方基础数据模拟")
    print("  • 价格数据范围基于历史实际数据")
    print("  • 系统会自动尝试连接官方API并在失败时使用基础数据")
    print("="*60)
