"""Rotating versus sticky: a new IP on every request, or one IP for the whole session.

    export FUSION_USER=... FUSION_PASS=...
    python 05_sticky_session.py
"""
import os
import random

import requests

USER, PASS = os.environ["FUSION_USER"], os.environ["FUSION_PASS"]
COUNTRY = os.environ.get("FUSION_COUNTRY", "us")


def ip_through(username: str, attempts: int = 3) -> str:
    proxy = f"http://{username}:{PASS}@resi.fusionproxy.net:12286"
    for attempt in range(attempts):
        try:
            # a fresh connection per call, so the gateway decides the IP each time
            with requests.Session() as s:
                return s.get("https://ipinfo.io/ip", proxies={"http": proxy, "https": proxy}, timeout=30).text.strip()
        except requests.RequestException:
            # residential IPs are real devices and a connection can drop; with a sticky
            # username the retry goes back to the same IP while the device is online
            if attempt == attempts - 1:
                raise


print("rotating:", [ip_through(f"{USER}-country-{COUNTRY}") for _ in range(3)])

sticky_user = f"{USER}-country-{COUNTRY}-sessid-{random.randint(1000000, 9999999)}-sessTime-600s"
print("sticky:  ", [ip_through(sticky_user) for _ in range(3)])
