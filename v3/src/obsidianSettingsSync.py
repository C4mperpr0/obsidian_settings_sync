import json
import os
import hashlib
from vault import Vault

class ObsidianSettingsSync:
    def __init__(self, config):
        self.CONFIG = config
        self.OBSIDIAN_CONFIG = self.load_obsidian_config(config)

    def load_obsidian_config(self, config):
        with open(config["obsidian-config-path"], "r") as file:
            return json.loads(file.read())

    def get_all_vaults(self):
        # cache values
        if hasattr(self, "_ALL_VAULTS"):
            return self._ALL_VAULTS

        vaults = []
        for v in self.OBSIDIAN_CONFIG["vaults"]:
            
            vaults.append(Vault(v, self.OBSIDIAN_CONFIG["vaults"][v]))
        self.ALL_VAULTS = vaults
        return vaults

    def copy(self, src, dst):
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy(src, dst)

    def get_vault_by_id(self, id):
        vaults = self.get_all_vaults()
        vault = list(filter(lambda vault: vault.id == id, vaults))
        if len(vault) == 1:
            return vault[0]
        else:
            return None

    def hash_string(s):
        sha512_hash_object = hashlib.sha512()
        sha512_hash_object.update( s.encode('utf-8') )
        return sha512_hash_object.hexdigest()
    
    def create_simlink(src, dst):
        if not src.endswith("/"):
            src += "/"
        if dst.endswith("/"):
            # cur of / at the end, because symlinks work that way
            dst = dst[:-1]
        os.symlink(src, dst)
