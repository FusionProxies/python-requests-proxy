"""Rotate through a list of proxies and move on when one fails.

By default the list is the public free proxy list from github.com/monosans/proxy-list.
Pass your own file as the first argument, one proxy per line (scheme://host:port or host:port).

    python 04_rotate_proxy_list.py [proxies.txt]
"""
import random
import sys

import requests

LIST_URL = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"


def load(path: str | None) -> list[str]:
    text = open(path, encoding="utf-8").read() if path else requests.get(LIST_URL, timeout=30).text
    out = []
    for line in text.split():
        out.append(line if "://" in line else "http://" + line)
    return out


def get(url: str, proxy_list: list[str], attempts: int = 8) -> requests.Response:
    for proxy in random.sample(proxy_list, min(attempts, len(proxy_list))):
        try:
            r = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=10)
            r.raise_for_status()
            print(f"ok    {proxy}")
            return r
        except requests.RequestException as e:
            print(f"fail  {proxy}  ({type(e).__name__})")
    raise RuntimeError(f"all {attempts} proxies failed")


proxies = load(sys.argv[1] if len(sys.argv) > 1 else None)
print(f"{len(proxies)} proxies loaded")
for _ in range(3):
    r = get("https://ipinfo.io/json", proxies)
    print("  exit IP:", r.json().get("ip"), r.json().get("country"))
