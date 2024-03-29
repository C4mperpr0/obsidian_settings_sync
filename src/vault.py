import os

class Vault:
    def __init__(self, id, json_data):
        self.id = id
        self.name = os.path.basename(os.path.normpath(json_data["path"]))
        self.path = json_data["path"]
        self.timestamp = json_data["ts"]
        self.is_open = json_data.get("open", False)

    def __repr__(self):
        return f"{self.id} | \"{self.name}\"{' <open>' if self.is_open else ''}"