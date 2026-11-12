"""Send one request through a proxy and print the IP the website sees.

    PROXY_URL=http://203.0.113.10:8080 python 01_basic_proxy.py
"""
import os
import sys

import requests

proxy = os.environ.get("PROXY_URL") or (sys.argv[1] if len(sys.argv) > 1 else None)
if not proxy:
    sys.exit("usage: PROXY_URL=http://host:port python 01_basic_proxy.py")

proxies = {"http": proxy, "https": proxy}  # key = scheme of the website, value = the proxy
r = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=30)
data = r.json()
print(f"{data['ip']} ({data.get('country')}, {data.get('org')})")
