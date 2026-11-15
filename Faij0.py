import threading
import time
import json
import os
import websocket
from flask import Flask, request, jsonify

app = Flask(__name__)

# Aapki Details
WS_URL = "https://i-875.olaparty.com" 
AUTH_TOKEN = "a0AehfTOl37ZAvyMPTQ04Q2oWhEai3QLhkD6VzMJ2z1uu-30qlyGWmSf2Tz-Agtz7tCkMJ9sjjbF04lUpL5Glmebof_NwphRav5D9U9h4hq2xPhovm_8nd9wvE8AtZJBlG5fEv2Rttx1j20bUj4MjQCQ9ul_weSiVSZEIF-7zaw4fUDcephwJmZ7GwRjsHpiwvzekZ4ToXX_kaqZBdFlcEi1W_Kt22nI2L4T0"
TARGET_UID = "4466035401"

ws_app = None

@app.route('/')
def home():
    return f"""
    <html>
        <head><title>OlaParty Bot Status</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h2 style="color: green;">✅ OlaParty Bot is Running 24/7!</h2>
            <p><b>Target UID:</b> {TARGET_UID}</p>
            <p>Status: Connected & Active</p>
        </body>
    </html>
    """

@app.route('/join', methods=['GET', 'POST'])
def join_endpoint():
    cid = request.args.get('cid') or (request.json.get('cid') if request.is_json else None)
    print(f"📥 Received join request with CID: {cid}")
    
    if ws_app and ws_app.sock and ws_app.sock.connected:
        try:
            payload = json.dumps({
                "type": "join",
                "cid": cid,
                "uid": TARGET_UID
            })
            ws_app.send(payload)
        except Exception as e:
            print(f"Error sending join payload: {e}")
            
    return jsonify({"status": "success", "message": "Join request processed", "cid": cid}), 200

def on_open(ws):
    print(f"✅ WebSocket Connected Successfully for UID: {TARGET_UID}!")
    
    def send_ping():
        while ws_app and ws_app.sock and ws_app.sock.connected:
            try:
                ping_data = json.dumps({
                    "type": "ping",
                    "uid": TARGET_UID
                })
                ws.send(ping_data)
                print(f"📤 Ping sent for UID {TARGET_UID}...")
                time.sleep(30)
            except Exception as e:
                print(f"⚠️ Ping error: {e}")
                break

    threading.Thread(target=send_ping, daemon=True).start()

def on_message(ws, message):
    print(f"📥 Received from WS: {message}")

def on_error(ws, error):
    print(f"❌ WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("⚠️ WebSocket Closed! Reconnecting in 5 seconds...")
    time.sleep(5)
    threading.Thread(target=start_websocket, daemon=True).start()

def start_websocket():
    global ws_app
    
    headers = {
        "token": AUTH_TOKEN,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)"
    }
    
    try:
        ws_app = websocket.WebSocketApp(
            WS_URL,
            header=headers,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        ws_app.run_forever(ping_interval=20, ping_timeout=10)
    except Exception as e:
        print(f"❌ Connection Exception: {e}")
        time.sleep(5)
        threading.Thread(target=start_websocket, daemon=True).start()

if __name__ == '__main__':
    ws_thread = threading.Thread(target=start_websocket)
    ws_thread.daemon = True
    ws_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
  
