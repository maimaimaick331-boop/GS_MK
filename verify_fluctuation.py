import time
import requests
import subprocess
import os

def run_collector():
    subprocess.run(["python", "backend/data_collector.py"], capture_output=True)

def get_latest_price():
    try:
        resp = requests.get("http://127.0.0.1:5000/api/price/latest")
        if resp.status_code == 200:
            data = resp.json()['data']
            # print(f"Debug: {data.keys()}")
            # if 'London' in data: print(f"Debug London: {data['London'].keys()}")
            return data
    except Exception as e:
        print(f"Error: {e}")
    return None

def main():
    print("Verifying price fluctuation...")
    
    run_collector()
    p1 = get_latest_price()
    if not p1: return
    
    time.sleep(1)
    
    run_collector()
    p2 = get_latest_price()
    if not p2: return
    
    metals = ['silver', 'gold', 'copper']
    markets = ['London', 'Comex']
    
    for market in markets:
        if market not in p1:
            print(f"[{market}] Missing market in data")
            continue
        for metal in metals:
            m_data1 = p1[market].get(metal)
            m_data2 = p2.get(market, {}).get(metal)
            
            if m_data1 and m_data2:
                v1 = m_data1.get('spot_price') or m_data1.get('futures_price')
                v2 = m_data2.get('spot_price') or m_data2.get('futures_price')
            
            if v1 and v2:
                diff = v2 - v1
                print(f"[{market}] {metal}: {v1:.4f} -> {v2:.4f} (Diff: {diff:+.4f})")
                if diff == 0:
                    print(f"!! WARNING: {metal} in {market} did not change!")
            else:
                print(f"[{market}] {metal}: Missing data")

if __name__ == "__main__":
    main()
