import json
import os

OBSIDIAN_CONFIG_PATH = "/home/carl/.config/obsidian/obsidian.json"

class Vault:
  def __init__(self, id, data):
    self.id = id
    self.name = os.path.basename(os.path.normpath(data["path"]))
    self.path = data["path"]
    self.timestamp = data["ts"]
    self.is_open = data.get("open", False)

  def __repr__(self):
    return f"{self.id} | \"{self.name}\"{' <open>' if self.is_open else ''}"

def load_config():
  with open(OBSIDIAN_CONFIG_PATH, "r") as file:
    return json.loads(file.read())

def get_all_vaults(config=load_config()):
  vaults = []
  for v in config["vaults"]:
    vaults.append(Vault(v, config["vaults"][v]))
  return vaults

vaults = get_all_vaults()
for v in vaults:
  print(v)