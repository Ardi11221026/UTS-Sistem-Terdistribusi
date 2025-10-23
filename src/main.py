import os
import time
import asyncio
import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List

from .models import Event
from .dedup_store import DedupStore
from .consumer import Consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

def create_app(db_path: str = None):
    db_path = db_path or os.environ.get("DEDUP_DB", "./data/dedup.db")
    dedup = DedupStore(db_path)
    queue: asyncio.Queue = asyncio.Queue()
    stats = {
        "received": 0,
        "unique_processed": 0,
        "duplicate_dropped": 0,
        "topics": set(),
        "start_time": time.time(),
    }

    consumer = Consumer(queue, dedup, stats)
    consumer_task = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal consumer_task
        logger.info("🔧 Starting lifespan...")

        # Startup: jalankan consumer di background
        consumer_task = asyncio.create_task(consumer.start())
        logger.info("✅ Background consumer started")
        yield
        # Shutdown
        consumer_task.cancel()
        await consumer.stop()
        dedup.close()
        logger.info("🔻 Consumer stopped and DB closed")

    app = FastAPI(title="UTS Pub-Sub Aggregator", lifespan=lifespan)

    @app.post("/publish")
    async def publish(request: Request):
        body = await request.json()
        events = body if isinstance(body, list) else [body]
        validated = []
        for e in events:
            try:
                ev = Event(**e)
                validated.append(ev.model_dump())
            except Exception as ex:
                raise HTTPException(status_code=422, detail=f"Invalid event schema: {ex}")

        for ev in validated:
            stats["received"] += 1
            stats["topics"].add(ev["topic"])
            await queue.put(ev)
        return JSONResponse({"accepted": len(validated)})

    @app.get("/events")
    async def get_events(topic: str = None):
        rows = dedup.list_events(topic)
        result = [
            {
                "topic": r[0],
                "event_id": r[1],
                "timestamp": r[2],
                "source": r[3],
                "payload": json.loads(r[4] or "{}"),
            }
            for r in rows
        ]
        return result

    @app.get("/stats")
    async def get_stats():
        return {
            "received": stats["received"],
            "unique_processed": stats["unique_processed"],
            "duplicate_dropped": stats["duplicate_dropped"],
            "topics": list(stats["topics"]),
            "uptime_seconds": int(time.time() - stats["start_time"]),
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
