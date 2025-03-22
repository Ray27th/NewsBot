# supabase_handler.py

import os
import json
import time
import threading
import websocket
from supabase import create_client, Client

from log_handler import logger  # Assuming you have a logger() function

# Setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = "syai_news"  # Change as needed
SCHEMA = "public"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_data():
    try:
        response = supabase.table(TABLE).select("*").execute()
        return response.data
    except Exception as e:
        logger(f"[Supabase] Error fetching data: {e}")
        return []


def insert_data(record: dict):
    try:
        response = supabase.table(TABLE).insert(record).execute()
        return response.data
    except Exception as e:
        logger(f"[Supabase] Error inserting data: {e}")
        return []


# --- Realtime Setup ---
def start_realtime_listener():
    clean_url = SUPABASE_URL.replace("https://", "").replace("http://", "")
    ws_url = f"wss://{clean_url}/realtime/v1/websocket?apikey={SUPABASE_KEY}&vsn=1.0.0"

    def on_open(ws):
        logger("[Realtime] WebSocket opened")

        def send_heartbeat():
            ref = 3
            while True:
                msg = {
                    "topic": "phoenix",
                    "event": "heartbeat",
                    "payload": {},
                    "ref": str(ref),
                }
                ws.send(json.dumps(msg))
                ref += 1
                time.sleep(30)

        threading.Thread(target=send_heartbeat, daemon=True).start()

        topic = f"realtime:{SCHEMA}:{TABLE}"

        # Step 1: JOIN the channel
        join_msg = {"topic": topic, "event": "phx_join", "payload": {}, "ref": "1"}
        logger(f"[Realtime] Sending JOIN: {join_msg}")
        ws.send(json.dumps(join_msg))

        # Step 2: Subscribe to INSERT/UPDATE/DELETE
        for i, event_type in enumerate(["INSERT", "UPDATE", "DELETE"], start=2):
            sub_msg = {
                "topic": topic,
                "event": "postgres_changes",
                "payload": {"event": event_type, "schema": SCHEMA, "table": TABLE},
                "ref": f"sub_{event_type.lower()}",
            }
            logger(f"[Realtime] Sending subscription: {sub_msg}")
            ws.send(json.dumps(sub_msg))

    def on_message(ws, message):
        logger(f"[Realtime] Raw WebSocket Message: {message}")
        try:
            data = json.loads(message)
            if data.get("event") == "postgres_changes":
                payload = data.get("payload")
                logger(
                    f"[Realtime] Event: {payload['type']} — {json.dumps(payload, indent=2)}"
                )
        except Exception as e:
            logger(f"[Realtime] Message error: {e}")

    def on_error(ws, error):
        logger(f"[Realtime] Error: {error}")

    def on_close(ws, code, msg):
        logger("[Realtime] WebSocket closed")

    def run_ws():
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever(ping_interval=20, ping_timeout=10)

    # Run listener in background
    thread = threading.Thread(target=run_ws, daemon=True)
    thread.start()
    logger("[Realtime] Listener started")
