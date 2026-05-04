import asyncio
import websockets
import json
import time
import requests
from core.event import Event

class BinanceClient:
    def __init__(self, symbol, event_bus):
        self.symbol = symbol.lower()
        self.event_bus = event_bus

        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth"
        self.rest_url = f"https://api.binance.com/api/v3/depth?symbol={self.symbol.upper()}&limit=1000"

        self.last_update_id = None

    def get_snapshot(self):
        res = requests.get(self.rest_url)
        data = res.json()

        self.last_update_id = data["lastUpdateId"]

        return {
            "bids": data["bids"],
            "asks": data["asks"]
        }

    async def stream_depth(self):
        async with websockets.connect(self.ws_url) as ws:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)

                U = data["U"]
                u = data["u"]

                # Ignore outdated
                if u <= self.last_update_id:
                    continue
                
                self.last_update_id = u

                event = Event(
                    type="depth",
                    data={
                        "bids": data.get("b", []),
                        "asks": data.get("a", [])
                    },
                    ts=time.time_ns()
                )

                self.event_bus.publish(event)