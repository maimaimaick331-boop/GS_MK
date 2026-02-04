#!/usr/bin/env python3
"""
自动数据采集脚本
配置定时采集任务
"""

import schedule
import time
import logging
from datetime import datetime
from data_collector import collect_all_data

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scheduled_collection():
    """定时采集任务"""
    logger.info("=" * 60)
    logger.info(f"开始定时数据采集 - {datetime.now()}")
    logger.info("=" * 60)
    try:
        collect_all_data()
        logger.info("定时采集完成")
    except Exception as e:
        logger.error(f"定时采集失败: {str(e)}")

def start_scheduler():
    """启动定时任务调度器"""
    logger.info("启动定时任务调度器...")
    
    # 每1小时执行一次
    schedule.every(1).hours.do(scheduled_collection)
    
    # 每天08:00执行一次
    schedule.every().day.at("08:00").do(scheduled_collection)
    
    logger.info("已注册定时任务:")
    logger.info("  - 每1小时执行一次")
    logger.info("  - 每天08:00执行一次")
    
    # 保持调度器运行
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    try:
        start_scheduler()
    except KeyboardInterrupt:
        logger.info("定时任务已停止")
