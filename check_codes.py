from urllib import request
import re

def check_sina(codes):
    url = f"http://hq.sinajs.cn/list={','.join(codes)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req) as resp:
            content = resp.read().decode('gbk')
            print(content)
    except Exception as e:
        print(e)

check_sina(['nf_AG0', 'fx_usdcny', 'hf_HG'])
