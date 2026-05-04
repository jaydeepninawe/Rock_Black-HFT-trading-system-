import matplotlib.pyplot as plt
from collections import deque

class Visualizer:
    def __init__(self, max_points=100):
        self.prices = deque(maxlen=max_points)
        self.spreads = deque(maxlen=max_points)
        self.imbalances = deque(maxlen=max_points)

        plt.ion()
        self.fig, self.axs = plt.subplots(3, 1)

    def update(self, event):
        d = event.data

        self.prices.append(d["mid_price"])
        self.spreads.append(d["spread"])
        self.imbalances.append(d["imbalance"])

        self.render()

    def render(self):
        self.axs[0].clear()
        self.axs[0].plot(self.prices)
        self.axs[0].set_title("Mid Price")

        self.axs[1].clear()
        self.axs[1].plot(self.spreads)
        self.axs[1].set_title("Spread")

        self.axs[2].clear()
        self.axs[2].plot(self.imbalances)
        self.axs[2].set_title("Imbalance")

        plt.pause(0.01)