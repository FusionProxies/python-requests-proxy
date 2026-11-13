<p align="center">
  <a href="https://fusionproxy.net/?utm_source=github&utm_medium=referral&utm_campaign=python-requests-proxy">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/FusionProxies/.github/main/assets/logo-on-dark.png">
      <img src="https://raw.githubusercontent.com/FusionProxies/.github/main/assets/logo-on-light.png" alt="Fusion Proxy" height="52">
    </picture>
  </a>
</p>

# How to use a proxy with Python requests

A practical guide to proxies in Python `requests`: the `proxies` argument, proxy authentication, HTTPS and SOCKS5 proxies, sessions, environment variables, rotating proxies, sticky sessions and the errors you will meet. Every script in this repository runs as is.

## Contents

1. [Set a proxy for one request](#1-set-a-proxy-for-one-request)
2. [Proxy with username and password](#2-proxy-with-username-and-password)
3. [SOCKS5 proxy](#3-socks5-proxy)
4. [Proxy for a whole session](#4-proxy-for-a-whole-session)
5. [Proxy from environment variables](#5-proxy-from-environment-variables)
6. [Rotating proxies](#6-rotating-proxies)
7. [Sticky sessions: keep the same IP](#7-sticky-sessions-keep-the-same-ip)
8. [Errors and how to fix them](#8-errors-and-how-to-fix-them)

```bash
pip install -r requirements.txt
```

## 1. Set a proxy for one request

`requests` takes a `proxies` dictionary. The **key** is the scheme of the website you request, the **value** is the proxy URL:

```python
import requests

proxies = {
    "http": "http://203.0.113.10:8080",   # used for http:// websites
    "https": "http://203.0.113.10:8080",  # used for https:// websites
}
r = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=30)
print(r.json()["ip"])
```

A common mistake is writing `"https": "https://..."` because the site is HTTPS. The value describes how you talk to the **proxy**, and most proxies, including authenticated residential ones, are plain `http://` even for HTTPS websites: requests opens a `CONNECT` tunnel and TLS runs inside it.

Always set `timeout`. Without it a dead proxy can block your script forever.

Script: [`01_basic_proxy.py`](01_basic_proxy.py)

## 2. Proxy with username and password

Put the credentials in the proxy URL:

```python
proxy = "http://USERNAME:PASSWORD@resi.fusionproxy.net:12286"
r = requests.get("https://ipinfo.io/json", proxies={"http": proxy, "https": proxy}, timeout=30)
```

If the password contains `@`, `:`, `/` or `#`, URL-encode it, otherwise requests splits the URL in the wrong place:

```python
from urllib.parse import quote

proxy = f"http://{quote(username, safe='')}:{quote(password, safe='')}@resi.fusionproxy.net:12286"
```

Script: [`02_authenticated_proxy.py`](02_authenticated_proxy.py)

## 3. SOCKS5 proxy

SOCKS support needs one extra package (it is in `requirements.txt`):

```bash
pip install "requests[socks]"
```

```python
proxy = "socks5h://USERNAME:PASSWORD@resi.fusionproxy.net:5390"
r = requests.get("https://ipinfo.io/json", proxies={"http": proxy, "https": proxy}, timeout=30)
```

Use `socks5h://`, not `socks5://`. With `socks5h` the proxy resolves the host name, so the DNS lookup happens in the proxy's country and does not leak from your machine.

Script: [`03_socks5_proxy.py`](03_socks5_proxy.py)

## 4. Proxy for a whole session

A `Session` reuses connections and keeps cookies. Set the proxy once:

```python
session = requests.Session()
session.proxies.update({"http": proxy, "https": proxy})
session.get("https://example.com/login")
session.get("https://example.com/account")
```

Keep in mind that a session reuses the open tunnel. On a rotating proxy, requests that reuse a connection keep the IP of that connection, so use a sticky session (section 7) when the IP must stay the same on purpose, and a new session when it must change.

## 5. Proxy from environment variables

requests reads `HTTP_PROXY`, `HTTPS_PROXY` and `NO_PROXY` when no proxy is passed:

```bash
export HTTPS_PROXY="http://USERNAME:PASSWORD@resi.fusionproxy.net:12286"
export HTTP_PROXY="$HTTPS_PROXY"
export NO_PROXY="localhost,127.0.0.1"
python your_script.py
```

To ignore them in one session, set `session.trust_env = False`. This also explains the classic surprise "my script uses a proxy I never set": check `env | grep -i proxy`.

## 6. Rotating proxies

There are two ways to get a new IP on every request.

**A rotating gateway.** One endpoint, a new residential IP per connection. Nothing to manage in your code:

```python
proxy = "http://USERNAME-country-us:PASSWORD@resi.fusionproxy.net:12286"
for _ in range(3):
    print(requests.get("https://ipinfo.io/ip", proxies={"http": proxy, "https": proxy}, timeout=30).text)
# three different US IPs
```

**A list of proxies.** Pick one per request and move on when it fails:

```python
import random

def get(url, proxy_list, attempts=5):
    for proxy in random.sample(proxy_list, min(attempts, len(proxy_list))):
        try:
            return requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=10)
        except requests.RequestException:
            continue
    raise RuntimeError("all proxies failed")
```

Script: [`04_rotate_proxy_list.py`](04_rotate_proxy_list.py) loads a list (by default the public [monosans/proxy-list](https://github.com/monosans/proxy-list)) and retries through it.

## 7. Sticky sessions: keep the same IP

Logins, carts and multi-step forms break when the IP changes in the middle. With a residential gateway you keep one IP by adding a session ID to the username:

```python
session_user = "USERNAME-country-us-sessid-4821937-sessTime-600s"  # same IP for 10 minutes
proxy = f"http://{session_user}:PASSWORD@resi.fusionproxy.net:12286"
```

Same `sessid` = same IP; a new `sessid` = a new IP. The format is explained in the [endpoint generator guide](https://fusionproxy.net/guides/endpoint-generator?utm_source=github&utm_medium=referral&utm_campaign=python-requests-proxy).

Script: [`05_sticky_session.py`](05_sticky_session.py)

## 8. Errors and how to fix them

| Error | Meaning | Fix |
|---|---|---|
| `ProxyError: ... 407 Proxy Authentication Required` | The proxy rejected the username or password | Check the credentials and URL-encode special characters |
| `ProxyError: Cannot connect to proxy` | The proxy host or port does not answer | Wrong port, proxy offline, or a firewall in between |
| `ConnectTimeout` / `ReadTimeout` | No answer within `timeout` | Try another proxy or raise the timeout for slow targets |
| `SSLError: certificate verify failed` | Something in the path presents its own certificate | Do not set `verify=False` to hide it; a proxy that breaks TLS is reading your traffic. Use another proxy |
| `InvalidSchema: Missing dependencies for SOCKS support` | SOCKS used without PySocks | `pip install "requests[socks]"` |
| `403` or `429` from the website | The site blocks or rate-limits the IP | Slow down, send normal browser headers, use a residential IP in the right country |

To test a proxy without writing code, use the free [online proxy checker](https://fusionproxy.net/tools/proxy-checker?utm_source=github&utm_medium=referral&utm_campaign=python-requests-proxy) or the [proxy-checker](https://github.com/FusionProxies/proxy-checker) command-line tool.

## Run the examples

```bash
export FUSION_USER="your_username"   # from the Fusion Proxy dashboard
export FUSION_PASS="your_password"
python 02_authenticated_proxy.py
```

Don't have proxy credentials? [Fusion Proxy residential proxies](https://fusionproxy.net/proxies/residential?utm_source=github&utm_medium=referral&utm_campaign=python-requests-proxy) start at $2.95/GB, and there is a [free trial](https://fusionproxy.net/free-trial?utm_source=github&utm_medium=referral&utm_campaign=python-requests-proxy). `01_basic_proxy.py` and `04_rotate_proxy_list.py` work with any proxy.

## Related

- [nodejs-proxy](https://github.com/FusionProxies/nodejs-proxy): the same in Node.js (fetch and axios)
- [curl-proxy](https://github.com/FusionProxies/curl-proxy): proxies with cURL
- [python-requests-retry](https://github.com/FusionProxies/python-requests-retry): retries and backoff in requests
- [python-web-scraping](https://github.com/FusionProxies/python-web-scraping): a complete scraper with requests and BeautifulSoup

## License

MIT, see [LICENSE](LICENSE).
