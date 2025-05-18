from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import requests
import asyncio
import websockets
import json
from bitcoinlib.wallets import Wallet
from bitcoinlib.services.services import Service
import logging
from datetime import datetime, timedelta, timezone
import random
import socket
import threading
import psutil
import os

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mempool.space API endpoints
MEMPOOL_API = "https://mempool.space/api/v1/fees/recommended"
MEMPOOL_MEMPOOL = "https://mempool.space/api/mempool"
DIFFICULTY_API = "https://mempool.space/api/v1/difficulty-adjustment"
SERVICE = Service()

# Simulated default data for offline mode
DEFAULT_DATA = {
    "fees": {
        "fastestFee": 50,
        "halfHourFee": 30,
        "hourFee": 20,
        "minimumFee": 10
    },
    "mempool": {
        "count": 5000,
        "vsize": 1000000
    },
    "savings": 0.0005,
    "difficulty": 88000000000000,  # Simulated difficulty in terahashes
    "adjustmentTime": datetime.now(timezone.utc).isoformat()
}

# Store historical data (in-memory for simplicity)
fee_history = []
mempool_history = []
tx_volume_history = []

def fetch_mempool_data():
    try:
        # Fetch fee data
        fee_response = requests.get(MEMPOOL_API, timeout=5)
        fee_response.raise_for_status()
        fee_data = fee_response.json()

        # Fetch mempool data
        mempool_response = requests.get(MEMPOOL_MEMPOOL, timeout=5)
        mempool_response.raise_for_status()
        mempool_data = mempool_response.json()

        # Fetch difficulty data
        difficulty_response = requests.get(DIFFICULTY_API, timeout=5)
        difficulty_response.raise_for_status()
        difficulty_data = difficulty_response.json()

        # Calculate potential savings
        savings = (fee_data["fastestFee"] - fee_data["hourFee"]) * 0.0001

        # Simulate transaction volume
        volume = random.uniform(100, 1000)  # BTC, for demo purposes

        data = {
            "fees": {
                "fastestFee": fee_data["fastestFee"],
                "halfHourFee": fee_data["halfHourFee"],
                "hourFee": fee_data["hourFee"],
                "minimumFee": fee_data["minimumFee"]
            },
            "mempool": {
                "count": mempool_data["count"],
                "vsize": mempool_data["vsize"]
            },
            "savings": savings,
            "difficulty": difficulty_data.get("difficulty", DEFAULT_DATA["difficulty"]),
            "adjustmentTime": difficulty_data.get("time", DEFAULT_DATA["adjustmentTime"])
        }

        # Update historical data
        timestamp = datetime.now(timezone.utc).isoformat()
        fee_history.append({"timestamp": timestamp, "hourFee": fee_data["hourFee"]})
        mempool_history.append({"timestamp": timestamp, "count": mempool_data["count"]})
        tx_volume_history.append({"timestamp": timestamp, "volume": volume})

        # Keep only last 24 hours of data
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        fee_history[:] = [entry for entry in fee_history if datetime.fromisoformat(entry["timestamp"]) > cutoff]
        mempool_history[:] = [entry for entry in mempool_history if datetime.fromisoformat(entry["timestamp"]) > cutoff]
        tx_volume_history[:] = [entry for entry in tx_volume_history if datetime.fromisoformat(entry["timestamp"]) > cutoff]

        logger.info(f"Successfully fetched mempool data: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        logger.error(f"Error fetching mempool data: {e}")
        return DEFAULT_DATA

@app.route('/network-data')
def network_data():
    try:
        data = fetch_mempool_data()
        logger.info(f"Network data served: {json.dumps(data, indent=2)}")
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in network-data endpoint: {e}")
        return jsonify(DEFAULT_DATA), 200

@app.route('/fee-history')
def fee_history_route():
    try:
        if fee_history:
            # Ensure at least one low-fee entry for testing
            now = datetime.now(timezone.utc)
            low_fee_exists = any(entry["hourFee"] < 15 for entry in fee_history)
            if not low_fee_exists:
                fee_history.append({
                    "timestamp": (now - timedelta(minutes=30)).isoformat(),
                    "hourFee": 14
                })
            logger.info(f"Fee history served: {len(fee_history)} entries, low fee included: {low_fee_exists}")
            return jsonify(fee_history)
        else:
            now = datetime.now(timezone.utc)
            simulated_history = [
                {
                    "timestamp": (now - timedelta(hours=i)).isoformat(),
                    "hourFee": random.randint(10, 50) if i != 0 else 14  # Low fee at current hour
                } for i in range(24)
            ]
            logger.info(f"Simulated fee history served: {len(simulated_history)} entries")
            return jsonify(simulated_history)
    except Exception as e:
        logger.error(f"Error in fee-history endpoint: {e}")
        now = datetime.now(timezone.utc)
        simulated_history = [
            {
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "hourFee": random.randint(10, 50) if i != 0 else 14
            } for i in range(24)
        ]
        return jsonify(simulated_history), 200

@app.route('/mempool-history')
def mempool_history_route():
    try:
        logger.info(f"Mempool history served: {len(mempool_history)} entries")
        return jsonify(mempool_history)
    except Exception as e:
        logger.error(f"Error in mempool-history endpoint: {e}")
        now = datetime.now(timezone.utc)
        simulated_history = [
            {
                "timestamp": (now - timedelta(minutes=i*10)).isoformat(),
                "count": random.randint(3000, 10000)
            } for i in range(60)
        ]
        return jsonify(simulated_history), 200

@app.route('/tx-volume-history')
def tx_volume_history_route():
    try:
        logger.info(f"Transaction volume history served: {len(tx_volume_history)} entries")
        return jsonify(tx_volume_history)
    except Exception as e:
        logger.error(f"Error in tx-volume-history endpoint: {e}")
        now = datetime.now(timezone.utc)
        simulated_history = [
            {
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "volume": random.uniform(100, 1000)
            } for i in range(24)
        ]
        return jsonify(simulated_history), 200

@app.route('/test-data')
def test_data():
    try:
        now = datetime.now(timezone.utc)
        sample_data = {
            "fees": {
                "fastestFee": 60,
                "halfHourFee": 40,
                "hourFee": 25,
                "minimumFee": 15
            },
            "mempool": {
                "count": 6000,
                "vsize": 1200000
            },
            "savings": 0.0007,
            "difficulty": 90000000000000,
            "adjustmentTime": now.isoformat()
        }
        sample_fee_history = [
            {
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "hourFee": random.randint(10, 50) if i != 0 else 14
            } for i in range(24)
        ]
        sample_mempool_history = [
            {
                "timestamp": (now - timedelta(minutes=i*10)).isoformat(),
                "count": random.randint(3000, 10000)
            } for i in range(60)
        ]
        sample_tx_volume_history = [
            {
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "volume": random.uniform(100, 1000)
            } for i in range(24)
        ]
        logger.info("Test data served")
        return jsonify({
            "network": sample_data,
            "fee_history": sample_fee_history,
            "mempool_history": sample_mempool_history,
            "tx_volume_history": sample_tx_volume_history
        })
    except Exception as e:
        logger.error(f"Error in test-data endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def dashboard():
    logger.info("Serving dashboard.html from templates")
    return render_template('dashboard.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    logger.info(f"Serving static file: {filename}")
    return send_from_directory('static', filename)

async def websocket_handler(websocket, path):
    try:
        while True:
            data = fetch_mempool_data()
            await websocket.send(json.dumps(data))
            logger.info("WebSocket data sent")
            await asyncio.sleep(60)
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

async def start_websocket_server(port=8765):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("localhost", port))
            sock.close()
        except socket.error as e:
            logger.warning(f"Port {port} already in use: {e}")
            if port == 8765:
                logger.info("Trying alternative port 8766")
                return await start_websocket_server(port=8766)
            return

        server = await websockets.serve(websocket_handler, "localhost", port)
        logger.info(f"WebSocket server started on ws://localhost:{port}")
        await server.wait_closed()
    except Exception as e:
        logger.error(f"Failed to start WebSocket server on port {port}: {e}")

def run_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server())
    loop.run_forever()

def free_port(port):
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    logger.info(f"Terminating process {conn.pid} using port ${port}")
                    proc.terminate()
                    proc.wait(timeout=3)
                except psutil.NoSuchProcess:
                    logger.warning(f"Process ${conn.pid} using port ${port} no longer exists")
                except Exception as e:
                    logger.error(f"Error terminating process on port ${port}: ${e}")
    except Exception as e:
        logger.error(f"Error freeing port ${port}: ${e}")

if __name__ == '__main__':
    # Free ports 8765 and 8766
    free_port(8765)
    free_port(8766)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 8765))
        sock.close()
        websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
        websocket_thread.start()
    except socket.error as e:
        logger.warning(f"WebSocket server not started, port 8765 already in use: ${e}")
        free_port(8766)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("localhost", 8766))
            sock.close()
            websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
            websocket_thread.start()
        except socket.error as e:
            logger.warning(f"WebSocket server not started, port 8766 already in use: ${e}")
    
    app.run(debug=False, host='0.0.0.0', port=5000)