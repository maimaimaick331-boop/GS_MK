import sys
import os

# Add the current directory to sys.path so we can import config and models
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from models import Session, SilverPrice
    session = Session()
    latest = session.query(SilverPrice).order_by(SilverPrice.date.desc()).first()
    if latest:
        print(f"Latest record: Market={latest.market}, Metal={latest.metal}, Price={latest.spot_price}, Date={latest.date}")
    else:
        print("No records found in silver_price table.")
    
    count = session.query(SilverPrice).count()
    print(f"Total records: {count}")
    
    # Check distinct metals
    metals = session.query(SilverPrice.metal).distinct().all()
    print(f"Distinct metals: {[m[0] for m in metals]}")
    
    session.close()
except Exception as e:
    print(f"Error: {e}")
