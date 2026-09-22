"""Wall-clock publication schedule, persisted independently of Git revisions."""
import json
from pathlib import Path


class Schedule:
    def __init__(self, data: Path, interval: int):
        if interval < 30:
            raise ValueError('PUBLISH_INTERVAL_SECONDS 必须至少为 30')
        self.path = data / 'schedule.json'
        self.interval = interval
        state = json.loads(self.path.read_text()) if self.path.exists() else {}
        last = state.get('last_started_at')
        self.next_at = 0 if last is None else last + interval

    def due(self, now: float) -> bool:
        return now >= self.next_at

    def started(self, now: float):
        self.next_at = now + self.interval
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'last_started_at': now, 'next_publish_at': self.next_at,
                                         'interval_seconds': self.interval}))
        temporary.chmod(0o600)
        temporary.replace(self.path)
