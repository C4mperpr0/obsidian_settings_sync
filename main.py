import json

OBSIDIAN_CONFIG_PATH = "/home/carl/.config/obsidian/obsidian.json"

class Vault:
  def __init__(data):
    self.id = data.keys()[0]
    self.path = data[0]["path"]
    self.timestamp = data[0]["ts"]
    self.is_open = data[0]["open"]

def load_config():
  with open(OBSIDIAN_CONFIG_PATH, "r") as file:
    return json.loads(file.read())

conf = load_config()
print(conf["vaults"])
vault = Vault(conf["vaults"][0])
print(vault)