"""
配置文件
"""
import os
from datetime import datetime

# 基础配置
class Config:
    # 数据库配置
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'silver_gold.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据采集配置
    DATA_UPDATE_INTERVAL = 3600  # 1小时更新一次
    
    # API配置
    FLASK_ENV = 'development'
    DEBUG = True
    JSON_AS_ASCII = False
    
    # 数据源URL
    COMEX_WAREHOUSE_URL = 'https://www.cmegroup.com/market-data/datamine/open-interest.html'
    LONDON_SILVER_URL = 'https://www.lbma.org.uk/precious-metals/statistics'
    
    # 缓存配置
    CACHE_ENABLED = True
    CACHE_TIMEOUT = 3600

# 开发环境
class DevelopmentConfig(Config):
    DEBUG = True

# 生产环境
class ProductionConfig(Config):
    DEBUG = False

config = DevelopmentConfig()
