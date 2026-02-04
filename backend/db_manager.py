"""
数据库管理工具
用于管理和维护SQLite数据库
"""

import sqlite3
import os
from datetime import datetime, timedelta
import argparse

DB_PATH = 'data/silver_gold.db'

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def backup_database():
    """备份数据库"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'data/backup/silver_gold_{timestamp}.db'
    
    # 创建备份目录
    os.makedirs('data/backup', exist_ok=True)
    
    conn = get_db()
    backup_conn = sqlite3.connect(backup_path)
    conn.backup(backup_conn)
    backup_conn.close()
    conn.close()
    
    print(f"✓ 数据库备份完成: {backup_path}")

def cleanup_old_logs(days=90):
    """清理旧日志"""
    conn = get_db()
    cursor = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    cursor.execute(
        "DELETE FROM data_log WHERE created_at < ?",
        (cutoff_date.isoformat(),)
    )
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✓ 已删除 {deleted} 条旧日志记录 (超过 {days} 天)")

def cleanup_old_data(days=365):
    """清理旧数据"""
    conn = get_db()
    cursor = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    tables = [
        'comex_warehouse',
        'silver_etf',
        'silver_price',
        'gold_data'
    ]
    
    total_deleted = 0
    for table in tables:
        cursor.execute(
            f"DELETE FROM {table} WHERE created_at < ?",
            (cutoff_date.isoformat(),)
        )
        total_deleted += cursor.rowcount
        print(f"  {table}: 删除 {cursor.rowcount} 条记录")
    
    conn.commit()
    conn.close()
    
    print(f"✓ 已删除总共 {total_deleted} 条旧数据 (超过 {days} 天)")

def get_statistics():
    """获取数据库统计信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    print("\n📊 数据库统计信息:")
    print("=" * 50)
    
    tables = [
        ('comex_warehouse', 'COMEX库存记录'),
        ('silver_etf', 'ETF持仓记录'),
        ('silver_price', '价格记录'),
        ('gold_data', '分析数据记录'),
        ('data_log', '采集日志')
    ]
    
    for table, label in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        
        # 获取最新和最旧的记录时间
        cursor.execute(f"SELECT MIN(created_at) as oldest FROM {table}")
        oldest = cursor.fetchone()['oldest']
        
        cursor.execute(f"SELECT MAX(created_at) as newest FROM {table}")
        newest = cursor.fetchone()['newest']
        
        print(f"\n{label}:")
        print(f"  总记录数: {count}")
        if oldest:
            print(f"  最旧记录: {oldest}")
        if newest:
            print(f"  最新记录: {newest}")
    
    # 数据库文件大小
    size = os.path.getsize(DB_PATH) / 1024 / 1024  # MB
    print(f"\n💾 数据库文件大小: {size:.2f} MB")
    
    conn.close()

def optimize_database():
    """优化数据库"""
    conn = get_db()
    cursor = conn.cursor()
    
    print("优化数据库中...")
    
    # 清理碎片
    cursor.execute("VACUUM")
    
    # 分析表以优化查询
    cursor.execute("ANALYZE")
    
    # 创建索引（如果不存在）
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_comex_date ON comex_warehouse(date)",
        "CREATE INDEX IF NOT EXISTS idx_etf_date ON silver_etf(date)",
        "CREATE INDEX IF NOT EXISTS idx_etf_name ON silver_etf(etf_name)",
        "CREATE INDEX IF NOT EXISTS idx_price_market ON silver_price(market)",
        "CREATE INDEX IF NOT EXISTS idx_price_date ON silver_price(date)",
        "CREATE INDEX IF NOT EXISTS idx_gold_category ON gold_data(category)",
        "CREATE INDEX IF NOT EXISTS idx_log_date ON data_log(created_at)",
    ]
    
    for idx in indexes:
        cursor.execute(idx)
    
    conn.commit()
    conn.close()
    
    print("✓ 数据库优化完成")

def export_to_csv(table):
    """导出表数据为CSV"""
    import csv
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {table}")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    
    filename = f"export_{table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(row)
    
    print(f"✓ 已导出 {len(rows)} 条记录到 {filename}")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='数据库管理工具')
    subparsers = parser.add_subparsers(dest='command')
    
    # 备份命令
    subparsers.add_parser('backup', help='备份数据库')
    
    # 清理旧日志
    cleanup_logs = subparsers.add_parser('cleanup-logs', help='清理旧日志')
    cleanup_logs.add_argument('--days', type=int, default=90, help='清理多少天前的日志')
    
    # 清理旧数据
    cleanup_data = subparsers.add_parser('cleanup-data', help='清理旧数据')
    cleanup_data.add_argument('--days', type=int, default=365, help='清理多少天前的数据')
    
    # 统计信息
    subparsers.add_parser('stats', help='显示数据库统计信息')
    
    # 优化数据库
    subparsers.add_parser('optimize', help='优化数据库')
    
    # 导出数据
    export = subparsers.add_parser('export', help='导出表数据为CSV')
    export.add_argument('table', help='表名')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        backup_database()
    elif args.command == 'cleanup-logs':
        cleanup_old_logs(args.days)
    elif args.command == 'cleanup-data':
        cleanup_old_data(args.days)
    elif args.command == 'stats':
        get_statistics()
    elif args.command == 'optimize':
        optimize_database()
    elif args.command == 'export':
        export_to_csv(args.table)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
