import os
import json

def default_config():
    return {
            "obsidian-config-path": "",
            "settings": {
                "full-check": True,
                "auto-open-vault": True,
                "master-vault": "",
                "sync": [
                    ".obsidian/plugins/",
                    ".obsidian/appearance.json",
                    ".obsidian/community-plugins.json",
                    ".obsidian/types.json"
                    ],
                "vault-config-hashes": {},
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