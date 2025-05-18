from flask import Flask, jsonify, render_template, send_from_directory, request, session
from flask_cors import CORS
import requests
import asyncio
import websockets
import json
import logging
from datetime import datetime, timedelta, timezone
import random
import socket
import threading
import psutil
import os
import bcrypt

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5000"]}})
app.secret_key = os.urandom(24).hex()
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mempool.space API endpoints
MEMPOOL_API = "https://mempool.space/api/v1/fees/recommended"
MEMPOOL_MEMPOOL = "https://mempool.space/api/mempool"
DIFFICULTY_API = "https://mempool.space/api/v1/difficulty-adjustment"

# Simulated default data
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
    "difficulty": 88000000000000,
    "adjustmentTime": datetime.now(timezone.utc).isoformat()
}

# Store historical data
fee_history = []
mempool_history = []
tx_volume_history = []

# In-memory user store
users = {}

def fetch_mempool_data():
    try:
        fee_response = requests.get(MEMPOOL_API, timeout=5)
        fee_response.raise_for_status()
        fee_data = fee_response.json()

        mempool_response = requests.get(MEMPOOL_MEMPOOL, timeout=5)
        mempool_response.raise_for_status()
        mempool_data = mempool_response.json()

        difficulty_response = requests.get(DIFFICULTY_API, timeout=5)
        difficulty_response.raise_for_status()
        difficulty_data = difficulty_response.json()

        savings = (fee_data["fastestFee"] - fee_data["hourFee"]) * 0.0001
        volume = random.uniform(100, 1000)

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

        timestamp = datetime.now(timezone.utc).isoformat()
        fee_history.append({"timestamp": timestamp, "hourFee": fee_data["hourFee"]})
        mempool_history.append({"timestamp": timestamp, "count": mempool_data["count"]})
        tx_volume_history.append({"timestamp": timestamp, "volume": volume})

        # Keep last 60 minutes for all histories
        cutoff_60m = datetime.now(timezone.utc) - timedelta(minutes=60)
        fee_history[:] = [entry for entry in fee_history if datetime.fromisoformat(entry["timestamp"]) > cutoff_60m]
        mempool_history[:] = [entry for entry in mempool_history if datetime.fromisoformat(entry["timestamp"]) > cutoff_60m]
        tx_volume_history[:] = [entry for entry in tx_volume_history if datetime.fromisoformat(entry["timestamp"]) > cutoff_60m]

        logger.info(f"Fetched mempool data")
        return data
    except Exception as e:
        logger.error(f"Error fetching mempool data: {e}")
        return DEFAULT_DATA

@app.route('/network-data')
def network_data():
    try:
        data = fetch_mempool_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in network-data endpoint: {e}")
        return jsonify(DEFAULT_DATA), 200

@app.route('/fee-history')
def fee_history_route():
    try:
        if fee_history:
            now = datetime.now(timezone.utc)
            low_fee_exists = any(entry["hourFee"] < 15 for entry in fee_history)
            if not low_fee_exists:
                fee_history.append({
                    "timestamp": (now - timedelta(minutes=30)).isoformat(),
                    "hourFee": 14
                })
            return jsonify(fee_history)
        else:
            now = datetime.now(timezone.utc)
            simulated_history = [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "hourFee": random.randint(10, 50) if i != 0 else 14
                } for i in range(60)
            ]
            return jsonify(simulated_history)
    except Exception as e:
        logger.error(f"Error in fee-history endpoint: {e}")
        return jsonify([
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=i)).isoformat(),
                "hourFee": random.randint(10, 50) if i != 0 else 14
            } for i in range(60)
        ]), 200

@app.route('/mempool-history')
def mempool_history_route():
    try:
        if mempool_history:
            return jsonify(mempool_history)
        else:
            now = datetime.now(timezone.utc)
            simulated_history = [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "count": random.randint(3000, 10000)
                } for i in range(60)
            ]
            return jsonify(simulated_history)
    except Exception as e:
        logger.error(f"Error in mempool-history endpoint: {e}")
        return jsonify([
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=i)).isoformat(),
                "count": random.randint(3000, 10000)
            } for i in range(60)
        ]), 200

@app.route('/tx-volume-history')
def tx_volume_history_route():
    try:
        if tx_volume_history:
            return jsonify(tx_volume_history)
        else:
            now = datetime.now(timezone.utc)
            simulated_history = [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "volume": random.uniform(100, 1000)
                } for i in range(60)
            ]
            return jsonify(simulated_history)
    except Exception as e:
        logger.error(f"Error in tx-volume-history endpoint: {e}")
        return jsonify([
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=i)).isoformat(),
                "volume": random.uniform(100, 1000)
            } for i in range(60)
        ]), 200

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
                "timestamp": (now - timedelta(minutes=i)).isoformat(),
                "hourFee": random.randint(10, 50) if i != 0 else 14
            } for i in range(60)
        ]
        sample_mempool_history = [
            {
                "timestamp": (now - timedelta(minutes=i)).isoformat(),
                "count": random.randint(3000, 10000)
            } for i in range(60)
        ]
        sample_tx_volume_history = [
            {
                "timestamp": (now - timedelta(minutes=i)).isoformat(),
                "volume": random.uniform(100, 1000)
            } for i in range(60)
        ]
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
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/session')
def session_check():
    username = session.get('username')
    if username:
        return jsonify(username=username)
    else:
        return jsonify(error="Not logged in"), 401

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logger.warning("Login attempt with missing username or password")
            return jsonify({'error': 'Username and password are required'}), 400

        if username in users:
            hashed_password = users[username]['password']
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                session['username'] = username
                session.permanent = True
                logger.info(f"Successful login for user: {username}")
                return jsonify({'message': 'Login successful', 'username': username}), 200
            else:
                logger.warning(f"Invalid password for user: {username}")
                return jsonify({'error': 'Invalid username or password'}), 401
        else:
            logger.warning(f"User not found: {username}")
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        logger.error(f"Error in login endpoint: {e}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    try:
        username = session.get('username')
        session.clear()
        logger.info(f"Successful logout for user: {username}")
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        logger.error(f"Error in logout endpoint: {e}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not username or not password or not confirm_password:
            logger.warning("Registration attempt with missing fields")
            return jsonify({'error': 'All fields are required'}), 400

        if password != confirm_password:
            logger.warning("Registration attempt with mismatched passwords")
            return jsonify({'error': 'Passwords do not match'}), 400

        if username in users:
            logger.warning(f"Registration attempt with existing username: {username}")
            return jsonify({'error': 'Username already exists'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users[username] = {'password': hashed_password}
        logger.info(f"Successful registration for user: {username}")
        return jsonify({'message': 'Registration successful, please login'}), 201
    except Exception as e:
        logger.error(f"Error in register endpoint: {e}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'Server is running'}), 200

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

async def websocket_handler(websocket, path):
    try:
        while True:
            data = fetch_mempool_data()
            await websocket.send(json.dumps(data))
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

if __name__ == "__main__":
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    
    app.run(debug=True)


def free_port(port):
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                pid = conn.pid
                if pid:
                    p = psutil.Process(pid)
                    p.terminate()  # or p.kill()
                    logger.info(f"Terminated process {pid} using port {port}")
                return True
        return False
    except Exception as e:
        logger.error(f"Error freeing port {port}: {e}")
        return False


if __name__ == '__main__':
    free_port(8765)
    free_port(8766)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 8765))
        sock.close()
        websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
        websocket_thread.start()
    except socket.error as e:
        logger.warning(f"WebSocket server not started, port 8765 already in use: {e}")
        free_port(8766)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("localhost", 8766))
            sock.close()
            websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
            websocket_thread.start()
        except socket.error as e:
            logger.warning(f"WebSocket server not started, port 8766 already in use: {e}")
    
    app.run(debug=False, host='0.0.0.0', port=5000)