import urllib.request
import urllib.error

def test_url(url, name):
    print(f"Testing {name}: {url}")
    try:
        req = urllib.request.Request(url)
        # Add headers to mimic a browser to avoid some basic anti-bot
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        req.add_header('Referer', 'https://finance.sina.com.cn/')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode('gbk') # Sina usually uses GBK
            print(f"Status: {response.status}")
            print(f"Content: {content.strip()}")
    except Exception as e:
        print(f"Error: {e}")

# 1. COMEX Silver Futures (New York)
# Sina Code: hf_SI
test_url("http://hq.sinajs.cn/list=hf_SI", "COMEX Silver (Sina)")

# 2. London Silver Spot (International)
# Sina Code: xagusd (Forex format) or similar. Let's try a few.
test_url("http://hq.sinajs.cn/list=hf_XAG", "London Silver 1 (hf_XAG)") 
test_url("http://hq.sinajs.cn/list=fx_sxagusd", "London Silver 2 (fx_sxagusd)")
