from sortedcontainers import SortedDict
from core.event import Event
import time

class OrderBook:
    def __init__(self, event_bus):
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.event_bus = event_bus

        self._best_bid = None
        self._best_ask = None

    def load_snapshot(self, snapshot):
        for price, qty in snapshot["bids"]:
            self.bids[float(price)] = float(qty)

        for price, qty in snapshot["asks"]:
            self.asks[float(price)] = float(qty)

    def process(self, event):
        if event.type != "depth":
            return

        # Update bids
        for price, qty in event.data["bids"]:
            price, qty = float(price), float(qty)

            if qty == 0:
                self.bids.pop(price, None)
            else:
                self.bids[price] = qty

        # Update asks
        for price, qty in event.data["asks"]:
            price, qty = float(price), float(qty)

            if qty == 0:
                self.asks.pop(price, None)
            else:
                self.asks[price] = qty

        if not self.bids or not self.asks:
            return

        self._best_bid = self.bids.peekitem(-1)[0]
        self._best_ask = self.asks.peekitem(0)[0]

     

        spread = self._best_ask - self._best_bid
        mid_price = (self._best_bid + self._best_ask) / 2

        imbalance = self.compute_imbalance()

        book_event = Event(
            type="book_update",
            data={
                "best_bid": self._best_bid,
                "best_ask": self._best_ask,
                "mid_price": mid_price,
                "spread": spread,
                "imbalance": imbalance
            },
            ts=time.time_ns()
        )

        self.event_bus.publish(book_event)

    def compute_imbalance(self):
        bid_vol = sum(self.bids.values())
        ask_vol = sum(self.asks.values())
        total = bid_vol + ask_vol
        return (bid_vol - ask_vol) / total if total > 0 else 0