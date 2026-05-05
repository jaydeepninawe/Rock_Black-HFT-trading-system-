from sortedcontainers import SortedDict
from core.event import Event
import time

class OrderBook:
    def __init__(self, event_bus):
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.event_bus = event_bus

    def load_snapshot(self, snapshot):
        for price, qty in snapshot["bids"]:
            self.bids[float(price)] = float(qty)

        for price, qty in snapshot["asks"]:
            self.asks[float(price)] = float(qty)

    def process(self, event):
        if event.type != "depth":
            return

        for price, qty in event.data["bids"]:
            price, qty = float(price), float(qty)
            if qty == 0:
                self.bids.pop(price, None)
            else:
                self.bids[price] = qty

        for price, qty in event.data["asks"]:
            price, qty = float(price), float(qty)
            if qty == 0:
                self.asks.pop(price, None)
            else:
                self.asks[price] = qty

        if not self.bids or not self.asks:
            return

        best_bid = self.bids.peekitem(-1)[0]
        best_ask = self.asks.peekitem(0)[0]

        # prevent invalid spread
        if best_ask <= best_bid:
            return

        spread = best_ask - best_bid
        mid_price = (best_bid + best_ask) / 2

        bid_vol = sum(self.bids.values())
        ask_vol = sum(self.asks.values())
        total = bid_vol + ask_vol
        imbalance = (bid_vol - ask_vol) / total if total > 0 else 0

        event = Event(
            type="book_update",
            data={
                "best_bid": best_bid,
                "best_ask": best_ask,
                "mid_price": mid_price,
                "spread": spread,
                "imbalance": imbalance
            },
            ts=time.time_ns()
        )

        self.event_bus.publish(event)