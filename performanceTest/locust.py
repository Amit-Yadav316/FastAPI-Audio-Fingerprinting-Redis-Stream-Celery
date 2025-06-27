import uuid
import json
import time
import random
import threading

from locust import HttpUser, task, between
from websocket import create_connection

import os

AUDIO_FILES = [
    os.path.join(os.path.dirname(__file__), "test_audio.webm")
]


class WavvyUser(HttpUser):
    wait_time = between(0.5, 1)

    @task
    def user_flow(self):
        task_id = str(uuid.uuid4())
        ws_url = f"ws://localhost:8000/ws/subscribe/{task_id}"
        result_holder = {}

        def listen_ws():
            try:
                ws = create_connection(ws_url, timeout=150)
                result_holder["start_time"] = time.time()
                result = ws.recv()
                result_holder["result"] = result
                result_holder["duration"] = round(time.time() - result_holder["start_time"], 2)
                ws.close()
            except Exception as e:
                result_holder["result"] = f"WebSocket error: {e}"

        ws_thread = threading.Thread(target=listen_ws)
        ws_thread.start()

        filename = random.choice(AUDIO_FILES)
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "audio/webm")}
            data = {"task_id": task_id} 
            response = self.client.post(
                "/match",
                files=files,
                data=data,
                name="/match_audio"
            )

        ws_thread.join(timeout=150)

        if "result" in result_holder:
            print(f"[{task_id}] Match in {result_holder['duration']}s → {result_holder['result'][:80]}")
        else:
            print(f"[{task_id}] No result after 150s")

    def on_stop(self):
        print("User finished")