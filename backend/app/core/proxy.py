# IPRoyal Proxy Config — Rotating residential
import random
import string

PROXY_HOST = "geo.iproyal.com"
PROXY_PORT = 12321
PROXY_USER = "Y0pwc0SVtQUJytk4"
PROXY_PASS = "WeFt0BkMuXJCB8HE"

# Static URL (same IP)
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

def get_rotating_proxy() -> str:
    """New random IP each call via session rotation."""
    session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"http://{PROXY_USER}_country-dz_session-{session_id}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
