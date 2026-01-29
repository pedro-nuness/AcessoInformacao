import asyncio
import os
import json
import aiohttp
from app.core.db import init_db
from app.repository import fetch_pending_shipments, mark_shipment_sent

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DISPATCH_INTERVAL = int(os.getenv("DISPATCH_INTERVAL", "30"))  # seconds

# Using repository functions for DB access (centralized)

async def dispatch_pending():
    await init_db()
    while True:
        rows = await fetch_pending_shipments()
        for row in rows:
            proc_id = row["processing_id"]
            result = row["result"]
            shipment = row["shipment"]
            if WEBHOOK_URL:
                try:
                    async with aiohttp.ClientSession() as session:
                        resp = await session.post(WEBHOOK_URL, json={"id": str(proc_id), "result": result, "shipment": shipment})
                        if resp.status >= 200 and resp.status < 300:
                            await mark_shipment_sent(proc_id)
                            print(f"Dispatched shipment for id={proc_id}")
                        else:
                            print(f"Failed to dispatch id={proc_id}: status {resp.status}")
                except Exception as e:
                    print(f"Exception dispatching id={proc_id}: {e}")
        await asyncio.sleep(DISPATCH_INTERVAL)

if __name__ == "__main__":
    asyncio.run(dispatch_pending())