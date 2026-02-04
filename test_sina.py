import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sina(symbols):
    url = f"http://hq.sinajs.cn/list={','.join(symbols)}"
    headers = {"Referer": "http://finance.sina.com.cn"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        print(f"URL: {url}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

# 测试不同的符号
print("Testing Global Futures:")
test_sina(["hf_GC", "hf_SI", "hf_HG", "hf_XAU", "hf_XAG", "hf_CAD"])

print("\nTesting SHFE:")
test_sina(["AU0", "AG0", "CU0"])

print("\nTesting SHFE with hf_ (just in case):")
test_sina(["hf_AU", "hf_AG", "hf_CU"])
