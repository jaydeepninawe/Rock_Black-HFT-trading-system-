# HFT-Style Trading System

## Overview

A low-latency, event-driven trading system simulating HFT architecture using real-time market data.

## Features

- Real-time market data ingestion (Binance WebSocket)
- Level 2 Order Book reconstruction
- Event-driven architecture (pub-sub system)
- Real-time visualization (price, spread, imbalance)
- Snapshot + incremental update synchronization

## Tech Stack

- Python
- asyncio, websockets
- SortedDict (order book)
- matplotlib

## Architecture

Market Data → Event Bus → Order Book → Visualization

## Run

pip install -r requirements.txt  
python main.py
