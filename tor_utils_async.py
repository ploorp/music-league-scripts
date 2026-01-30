import aiohttp
import aiohttp_socks
import asyncio
import random
from stem import Signal
from stem.control import Controller

TOR_PROXIES = [
    "socks5://127.0.0.1:9050",
    "socks5://127.0.0.1:9052",
    "socks5://127.0.0.1:9054",
    "socks5://127.0.0.1:9056",
    "socks5://127.0.0.1:9058",
    "socks5://127.0.0.1:9060",
    "socks5://127.0.0.1:9062",
    "socks5://127.0.0.1:9064",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-GPC": "1",
}

CONTROL_PORTS = [9051, 9053, 9055, 9057]
CONTROL_PASSWORD = None

# --- GLOBAL CONNECTORS + SESSIONS ---

proxy_connectors = {}
proxy_sessions = {}

async def init_tor_sessions():
    """Initialize reusable ProxyConnectors and ClientSessions."""
    for proxy in TOR_PROXIES:
        conn = aiohttp_socks.ProxyConnector.from_url(proxy)
        session = aiohttp.ClientSession(connector=conn)
        proxy_connectors[proxy] = conn
        proxy_sessions[proxy] = session

async def close_tor_sessions():
    """Gracefully close all sessions on shutdown."""
    for session in proxy_sessions.values():
        await session.close()

# --- MAIN REQUEST FUNCTION ---

async def get_via_tor(url: str, retries: int = 3, timeout: int = 20) -> str:
    for attempt in range(retries):
        proxy = random.choice(TOR_PROXIES)
        session = proxy_sessions[proxy]

        try:
            async with session.get(url, headers=DEFAULT_HEADERS, timeout=timeout) as response:
                if response.status == 429:
                    await renew_tor_identity(proxy)
                    await asyncio.sleep(1)
                    continue

                response.raise_for_status()
                return await response.text()

        except Exception as e:
            print(f"[tor_utils_async] Attempt {attempt+1}/{retries} via {proxy} failed: {e}")
            await asyncio.sleep(1 + attempt)

    raise Exception(f"Failed to fetch {url} after {retries} attempts")

# --- TOR IDENTITY RENEWAL ---

async def renew_tor_identity(proxy_url: str | None = None):
    if not CONTROL_PORTS:
        return

    if proxy_url and proxy_url in TOR_PROXIES:
        idx = TOR_PROXIES.index(proxy_url) % len(CONTROL_PORTS)
    else:
        idx = random.randint(0, len(CONTROL_PORTS) - 1)

    port = CONTROL_PORTS[idx]

    try:
        with Controller.from_port(port=port) as c:
            if CONTROL_PASSWORD:
                c.authenticate(password=CONTROL_PASSWORD)
            else:
                c.authenticate()
            c.signal(Signal.NEWNYM)
    except Exception as e:
        print(f"[tor_utils_async] Failed to renew identity on port {port}: {e}")
