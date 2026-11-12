"""Proxy with a username and password, special characters URL-encoded.

    export FUSION_USER=... FUSION_PASS=...
    python 02_authenticated_proxy.py
"""
import os
from urllib.parse import quote

import requests

user = os.environ["FUSION_USER"] + "-country-" + os.environ.get("FUSION_COUNTRY", "us")
password = os.environ["FUSION_PASS"]

# quote() keeps characters like @ : / # in the password from breaking the URL
proxy = f"http://{quote(user, safe='')}:{quote(password, safe='')}@resi.fusionproxy.net:12286"

r = requests.get("https://ipinfo.io/json", proxies={"http": proxy, "https": proxy}, timeout=30)
data = r.json()
print(f"{data['ip']} ({data.get('country')}, {data.get('city')})")
