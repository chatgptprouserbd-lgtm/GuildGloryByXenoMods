import os
import json
import requests
from aiohttp import web
from guild import GuildSquadManager

app = web.Application()
manager = GuildSquadManager()

FIREBASE_URL = "https://xenomod-f51d7-default-rtdb.firebaseio.com"

def save_account_to_firebase(uid, access_token, region="BD"):
    try:
        # 1. Direct REST API request to save/update token in token_cache
        token_data = {
            "uid": str(uid),
            "access_token": access_token,
            "region": region
        }
        res_token = requests.put(
            f"{FIREBASE_URL}/token_cache/{uid}.json",
            json=token_data,
            timeout=10
        )

        # 2. Save account in accounts list
        acc_data = {
            "uid": str(uid),
            "region": region,
            "created_at": "2026-10-23 12:00:00"
        }
        res_acc = requests.put(
            f"{FIREBASE_URL}/accounts/{uid}.json",
            json=acc_data,
            timeout=10
        )

        if res_token.status_code == 200 and res_acc.status_code == 200:
            print(f"[✔] Successfully saved account {uid} to Firebase REST API", flush=True)
            return True, "Saved successfully"
        else:
            err_msg = f"Firebase Error Code: {res_token.status_code}"
            print(f"[-] {err_msg}", flush=True)
            return False, err_msg

    except Exception as e:
        print(f"[-] Firebase Save Exception: {e}", flush=True)
        return False, str(e)

async def index(request):
    return web.FileResponse('./templates/index.html')

async def handle_add_account(request):
    try:
        data = await request.post()
        uid = data.get("uid", "").strip()
        access_token = data.get("access_token", "").strip()
        region = data.get("region", "BD").strip().upper()

        if not uid or not access_token:
            return web.json_response({"status": "error", "message": "UID and Access Token are required!"}, status=400)

        success, msg = save_account_to_firebase(uid, access_token, region)
        if success:
            return web.json_response({"status": "success", "message": f"Account {uid} saved to Firebase successfully!"})
        else:
            return web.json_response({"status": "error", "message": f"Failed: {msg}"}, status=500)
    except Exception as e:
        print(f"[-] Route Error: {e}", flush=True)
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def handle_create_squad(request):
    try:
        data = await request.json()
        squad_name = data.get("squad_name")
        uids = data.get("uids", [])
        res = manager.create_squad(squad_name, uids)
        return web.json_response(res)
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def handle_guild_squad_join(request):
    try:
        data = await request.json()
        guild_id = data.get("guild_id")
        squad_name = data.get("squad_name")
        res = manager.join_guild_with_squad(guild_id, squad_name)
        return web.json_response(res)
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)

# Routes
app.router.add_get('/', index)
app.router.add_post('/api/add_account', handle_add_account)
app.router.add_post('/api/create_squad', handle_create_squad)
app.router.add_post('/api/guild_squad_join', handle_guild_squad_join)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)
