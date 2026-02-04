"""
数据模型定义
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
try:
    from config import config
except ImportError:
    from backend.config import config

# 创建数据库引擎
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class ComexWarehouse(Base):
    """COMEX仓库库存"""
    __tablename__ = 'comex_warehouse'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    metal = Column(String(20), default='silver', comment='金属类型')
    total_oz = Column(Float, comment='总库存（百万盎司/吨）')
    eligible_oz = Column(Float, comment='合格（百万盎司/吨）')
    registered_oz = Column(Float, comment='注册（百万盎司/吨）')
    price = Column(Float, comment='当日价格')
    
    # Debug & Audit 元信息
    source = Column(String(100), comment='数据源 (CME/LME/SHFE/SGE)')
    source_url = Column(String(500), comment='报表原始链接')
    report_date = Column(String(100), comment='报表日期 (asOf)')
    fetched_at = Column(DateTime, default=datetime.utcnow, comment='抓取时间')
    field_name = Column(String(100), comment='字段口径 (total/eligible/registered/on-warrant/cancelled)')
    cell_ref = Column(String(100), comment='单元格引用 (Sheet+Cell)')
    file_hash = Column(String(100), comment='原始文件SHA256哈希')
    quality = Column(String(50), comment='数据质量 (REALTIME/STALE/ERROR_DIFF/UNKNOWN_SPEC)')
    
    raw_payload = Column(String(4000), comment='原始数据提取内容')
    mapping = Column(String(1000), comment='映射逻辑说明')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SilverETF(Base):
    """白银ETF持仓数据"""
    __tablename__ = 'silver_etf'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    etf_name = Column(String(255), comment='ETF名称')
    holdings_oz = Column(Float, comment='持仓量（百万盎司）')
    yoy_change = Column(Float, comment='同比增长（%）')
    price = Column(Float, comment='当日价格')
    
    # Debug 元信息
    source = Column(String(100), comment='数据源')
    provider_as_of = Column(String(100), comment='数据源时间戳')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SilverPrice(Base):
    """现货/期货价格"""
    __tablename__ = 'silver_price'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    market = Column(String(50), comment='市场（London/Shanghai/Comex）')
    metal = Column(String(20), default='silver', comment='金属类型（silver/gold/copper）')
    spot_price = Column(Float, comment='现货价格')
    futures_price = Column(Float, comment='期货价格')
    premium = Column(Float, comment='溢价/贴水')
    premium_type = Column(String(20), comment='Premium/Backwardation')
    
    # Debug 元信息
    source = Column(String(100), comment='数据源')
    provider_as_of = Column(String(100), comment='数据源时间戳')
    field_used = Column(String(100), comment='使用的字段')
    quality = Column(String(50), comment='数据质量')
    raw_payload = Column(String(4000), comment='原始数据')
    mapping = Column(String(1000), comment='字段映射')
    is_error = Column(Integer, default=0, comment='是否数据异常')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GoldData(Base):
    """黄金基础数据"""
    __tablename__ = 'gold_data'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    category = Column(String(100), comment='分类（认知/逻辑/数据/风险）')
    indicator = Column(String(255), comment='指标名称')
    value = Column(Float, comment='数值')
    description = Column(String(1000), comment='描述')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DataLog(Base):
    """数据采集日志"""
    __tablename__ = 'data_log'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(100), comment='数据源')
    status = Column(String(20), comment='状态（success/fail）')
    message = Column(String(500), comment='消息')
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建表
def init_db():
    Base.metadata.create_all(engine)
    print("数据库初始化完成")

if __name__ == '__main__':
    init_db()
