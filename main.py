from dashboard_server import app
from aiohttp import web

if __name__ == "__main__":
    print("[*] DARK MASTER ENGINE WITH FIREBASE REALTIME DB STARTING...")
    web.run_app(app, host="0.0.0.0", port=8080)
