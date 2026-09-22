"""Credential import and read-only session heartbeat. Never log cookie values."""
import json
import re
import time
from pathlib import Path

from .content import Blocked


def parse_cookies(header: str) -> list[dict]:
    header = header.strip().replace('\\_', '_')
    if header.lower().startswith('cookie:'):
        header = header[7:].strip()
    cookies = {}
    for part in header.split(';'):
        name, sep, value = part.strip().partition('=')
        if not sep or not re.fullmatch(r'[A-Za-z0-9_-]+', name) or re.search(r'[\r\n\x00]', value):
            raise Blocked('Cookie 格式无效')
        if name in cookies:
            raise Blocked('Cookie 名称重复')
        cookies[name] = {'name': name, 'value': value, 'url': 'https://fanqienovel.com/',
                         'secure': True, 'sameSite': 'Lax'}
    if not {'sessionid', 'sid_tt'} & cookies.keys():
        raise Blocked('缺少登录会话 Cookie')
    return list(cookies.values())


def heartbeat_status(data: Path, ok: bool):
    path = data / 'heartbeat.json'
    previous = json.loads(path.read_text()) if path.exists() else {}
    now = time.time()
    status = {'ok': ok, 'checked_at': now,
              'last_success_at': now if ok else previous.get('last_success_at'),
              'consecutive_failures': 0 if ok else previous.get('consecutive_failures', 0) + 1}
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(status), encoding='utf-8')
    temporary.chmod(0o600)
    temporary.replace(path)


async def heartbeat(data, factory):
    try:
        async with factory() as site:
            await site.login()
        heartbeat_status(data, True)
    except Exception:
        heartbeat_status(data, False)
        raise
