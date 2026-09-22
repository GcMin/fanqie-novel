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
    raise SystemExit(0 if healthy(Path(os.getenv('DATA_DIR', '/data')), time.time(),
                                 int(os.getenv('HEARTBEAT_INTERVAL_SECONDS', '300'))) else 1)
