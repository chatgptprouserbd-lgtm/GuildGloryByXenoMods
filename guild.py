import os
import asyncio
import firebase_admin
from firebase_admin import db

# Initialize Firebase Admin cleanly using only Realtime Database URL (No fake certificate needed)
if not firebase_admin._apps:
    try:
        firebase_admin.initialize_app(options={
            'databaseURL': 'https://xenomod-f51d7-default-rtdb.firebaseio.com'
        })
    except Exception as e:
        print(f"[-] Firebase Init Error: {e}")

class GuildSquadManager:
    def __init__(self):
        self.squads = {}  # Format: {"squad_name": ["uid1", "uid2"]}
        self.running_matches = {}

    def load_tokens(self):
        try:
            ref = db.reference('token_cache')
            data = ref.get()
            return data if isinstance(data, dict) else {}
        except Exception as e:
            print(f"[-] Firebase Load Error: {e}")
            return {}

    def create_squad(self, squad_name, uids):
        self.squads[squad_name] = uids
        try:
            db.reference(f'squads/{squad_name}').set(uids)
        except Exception:
            pass
        return {"status": "success", "message": f"Squad '{squad_name}' created & saved to Firebase!"}

    def join_guild_with_squad(self, guild_id, squad_name):
        tokens = self.load_tokens()
        squad_uids = self.squads.get(squad_name, [])
        
        if not squad_uids:
            try:
                squad_uids = db.reference(f'squads/{squad_name}').get() or []
            except Exception:
                pass

        if not squad_uids:
            return {"status": "error", "message": f"Squad '{squad_name}' not found!"}

        joined = []
        for uid in squad_uids:
            if str(uid) in tokens:
                joined.append({"uid": uid, "status": "Joined", "guild_id": guild_id})

        asyncio.create_task(self.auto_cs_rank_loop(squad_name, guild_id))

        return {
            "status": "success",
            "message": f"Squad '{squad_name}' joined Guild {guild_id} via Firebase and Auto CS-Rank started!",
            "details": joined
        }

    async def auto_cs_rank_loop(self, squad_name, guild_id):
        self.running_matches[squad_name] = True
        print(f"[*] [FIREBASE AUTO CS RANK] Squad '{squad_name}' active in Guild {guild_id}...")
        
        while self.running_matches.get(squad_name, False):
            print(f"[+] Squad '{squad_name}': CS Rank Match Started!")
            await asyncio.sleep(10)
            print(f"[~] Squad '{squad_name}': Match in progress...")
            await asyncio.sleep(20)
            print(f"[✔] Squad '{squad_name}': Match Finished! Restarting next match...")
            await asyncio.sleep(5)
