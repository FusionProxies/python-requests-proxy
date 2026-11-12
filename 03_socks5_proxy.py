"""SOCKS5 proxy with requests. Needs: pip install "requests[socks]"

socks5h:// lets the proxy resolve host names, so DNS does not leak from your machine.

    export FUSION_USER=... FUSION_PASS=...
    python 03_socks5_proxy.py
"""
import os
from urllib.parse import quote

import requests

user = quote(os.environ["FUSION_USER"] + "-country-" + os.environ.get("FUSION_COUNTRY", "de"), safe="")
password = quote(os.environ["FUSION_PASS"], safe="")
proxy = f"socks5h://{user}:{password}@resi.fusionproxy.net:5390"

r = requests.get("https://ipinfo.io/json", proxies={"http": proxy, "https": proxy}, timeout=30)
data = r.json()
print(f"{data['ip']} ({data.get('country')}, {data.get('city')})")
