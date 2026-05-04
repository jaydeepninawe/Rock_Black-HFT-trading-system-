import threading
import asyncio
from core.event_bus import EventBus
from data_feed.binance_client import BinanceClient
from orderbook.order_book import OrderBook
from visualization.visualizer import Visualizer


def event_loop(order_queue, order_book):
    while True:
        event = order_queue.get()

        if event.type == "depth":
            order_book.process(event)


def main():
    event_bus = EventBus()

    order_queue = event_bus.register()
    visual_queue = event_bus.register()

    order_book = OrderBook(event_bus)
    visualizer = Visualizer()

    client = BinanceClient("btcusdt", event_bus)

    # ✅ Step 1: Load snapshot
    snapshot = client.get_snapshot()
    order_book.load_snapshot(snapshot)

    print("Snapshot loaded:", len(order_book.bids), len(order_book.asks))

    # Thread: order processing
    threading.Thread(
        target=event_loop,
        args=(order_queue, order_book),
        daemon=True
    ).start()

    # Thread: WebSocket
    threading.Thread(
        target=lambda: asyncio.run(client.stream_depth()),
        daemon=True
    ).start()

    # ✅ MAIN THREAD: visualization
    while True:
        event = visual_queue.get()

        if event.type == "book_update":
            visualizer.update(event)


if __name__ == "__main__":
    main()