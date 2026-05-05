from core.event import Event
import time
from core.logger import setup_logger

class ImbalanceStrategy:
    def __init__(self, event_bus, threshold=0.2):
        self.event_bus = event_bus
        self.threshold = threshold
        self.last_signal_time = 0
        self.logger = setup_logger()

    def process(self, event):
        if event.type != "book_update":
            return

        imbalance = event.data["imbalance"]

        # cooldown
        if time.time() - self.last_signal_time < 1:
            return

        if imbalance > self.threshold:
            action = "BUY"
        elif imbalance < -self.threshold:
            action = "SELL"
        else:
            return

        self.last_signal_time = time.time()

        # 🔥 LOG SIGNAL
        self.logger.info(f"{action} | imbalance={imbalance:.4f}")

        signal_event = Event(
            type="signal",
            data={
                "action": action,
                "imbalance": imbalance
            },
            ts=time.time_ns()
        )

        self.event_bus.publish(signal_event)