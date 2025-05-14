import os
import json

def default_config():
    return {
            "obsidian-config-path": "",
            "settings": {
                "sync": [
                    ".obsidian/plugins/",
                    ".obsidian/community-plugins.json"
                    ]
                },
                "synced-vaults": {}
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