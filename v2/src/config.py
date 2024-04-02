import os
import json

def default_config():
    return {
            "obsidian-config-path": "",
            "settings": {
                "versioning": True,
                "auto-open-vault": True,
                "sync": [
                    ".obsidian/plugins/",
                    ".obsidian/community-plugins.json"
                    ],
                "synced-vaults": [],
                "blacklisted-vaults": [],
                "sync-new-vaults": True
                }
            } 

def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as file:
            return json.loads(file.read())
    else:
        return None

def save_config(config):
    with open("config.json", "w+") as file:
        file.write(json.dumps(config, indent=4))