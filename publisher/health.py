"""Docker health check: no network requests and no credentials in output."""
import json
import os
import time
from pathlib import Path


def healthy(data, now, interval):
    try:
        state = json.loads((data / 'heartbeat.json').read_text())
        return state['ok'] is True and 0 <= now - state['checked_at'] <= max(30, interval) * 2 + 120
    except (OSError, ValueError, KeyError, TypeError):
        return False


if __name__ == '__main__':
    root = Path(os.getenv('DATA_DIR', '/data'))
    if os.getenv('NOVELS_CONFIG_PATH') and os.getenv('NOVEL_WORKER') != '1':
        from .novels import load_profiles
        try:
            profiles = load_profiles(Path(os.environ['NOVELS_CONFIG_PATH']))
            ok = all(healthy(root / 'novels' / p['id'], time.time(), p['heartbeat_interval_seconds']) for p in profiles)
        except Exception:
            ok = False
    else:
        ok = healthy(root, time.time(), int(os.getenv('HEARTBEAT_INTERVAL_SECONDS', '300')))
    raise SystemExit(0 if ok else 1)
