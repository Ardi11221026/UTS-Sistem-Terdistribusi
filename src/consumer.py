import asyncio
import json
import logging
from .dedup_store import DedupStore

logger = logging.getLogger("consumer")

class Consumer:
    def __init__(self, queue: asyncio.Queue, dedup_store: DedupStore, stats: dict):
        self.queue = queue
        self.dedup = dedup_store
        self.stats = stats
        self.running = True

    async def start(self):
        logger.info("🚀 Consumer started, waiting for events...")
        while self.running:
            try:
                ev = await self.queue.get()
                topic = ev["topic"]
                event_id = ev["event_id"]

                if self.dedup.is_processed(topic, event_id):
                    logger.info(f"⚠️ Duplicate detected: {topic}/{event_id}")
                    self.stats["duplicate_dropped"] += 1
                else:
                    self.dedup.mark_processed(
                        topic,
                        event_id,
                        ev.get("timestamp", ""),
                        ev.get("source", ""),
                        json.dumps(ev.get("payload", {})),
                    )
                    self.stats["unique_processed"] += 1
                    logger.info(f"✅ Processed unique event: {topic}/{event_id}")

                self.queue.task_done()
            except asyncio.CancelledError:
                logger.info("🛑 Consumer task cancelled")
                break
            except Exception as e:
                logger.exception(f"Consumer error: {e}")
                await asyncio.sleep(0.1)

    async def stop(self):
        logger.info("🔻 Stopping consumer...")
        self.running = False
