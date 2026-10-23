import os
from aiohttp import web
from guild import GuildSquadManager
from firebase_admin import db

app = web.Application()
manager = GuildSquadManager()

def save_account_to_firebase(uid, access_token, region="BD"):
    try:
        # 1. Save to accounts list node in Firebase
        acc_ref = db.reference('accounts')
        existing_accs = acc_ref.get() or []
        
        found = False
        if isinstance(existing_accs, list):
            for acc in existing_accs:
                if isinstance(acc, dict) and str(acc.get("uid")) == str(uid):
                    found = True
                    break
            if not found:
                existing_accs.append({"uid": uid, "region": region, "created_at": "2026-10-23 12:00:00"})
                acc_ref.set(existing_accs)
        elif isinstance(existing_accs, dict):
            acc_ref.child(str(uid)).set({"uid": uid, "region": region, "created_at": "2026-10-23 12:00:00"})

        # 2. Save to token_cache dictionary node in Firebase (Prevents corruption completely)
        token_ref = db.reference(f'token_cache/{uid}')
        token_ref.set({
            "uid": uid,
            "access_token": access_token,
            "region": region
        })
        return True
    except Exception as e:
        print(f"[-] Firebase Save Error: {e}")
        return False

async def index(request):
    return web.FileResponse('./templates/index.html')

async def handle_add_account(request):
    try:
        data = await request.post()
        uid = data.get("uid", "").strip()
        access_token = data.get("access_token", "").strip()
        region = data.get("region", "BD").strip().upper()

        if not uid or not access_token:
            return web.json_response({"status": "error", "message": "UID and Access Token required!"}, status=400)

        success = save_account_to_firebase(uid, access_token, region)
        if success:
            return web.json_response({"status": "success", "message": f"Account {uid} saved to Firebase successfully!"})
        else:
            return web.json_response({"status": "error", "message": "Failed to save to Firebase database."}, status=500)
    except Exception as e:
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
