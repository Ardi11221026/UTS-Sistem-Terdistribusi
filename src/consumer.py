import asyncio
import json
import logging
from .dedup_store import DedupStore

logger = logging.getLogger('consumer')

class Consumer:
    def __init__(self, queue: asyncio.Queue, dedup_store: DedupStore, stats: dict):
        self.queue = queue
        self.dedup = dedup_store
        self.stats = stats
        self._task = None
        self._stopped = False

    async def start(self):
        self._stopped = False
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._stopped = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self):
        while not self._stopped:
            try:
                ev = await self.queue.get()
                # ev is dict with fields: topic,event_id,timestamp,source,payload
                topic = ev['topic']
                event_id = ev['event_id']
                if self.dedup.is_processed(topic, event_id):
                    logger.info(f"Duplicate detected: {topic} / {event_id}")
                    self.stats['duplicate_dropped'] += 1
                else:
                    # simulate processing (fast)
                    self.dedup.mark_processed(topic, event_id, ev.get('timestamp',''), ev.get('source',''), json.dumps(ev.get('payload',{})))
                    self.stats['unique_processed'] += 1
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception('consumer error: %s', e)
                await asyncio.sleep(0.1)
