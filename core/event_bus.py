from queue import Queue

class EventBus:
    def __init__(self):
        self.subscribers = []

    def register(self):
        q = Queue()
        self.subscribers.append(q)
        return q

    def publish(self, event):
        for q in self.subscribers:
            q.put(event)