import json
import os
import hashlib
from vault import Vault

class ObsidianSettingsSync:
    def __init__(self, config):
        self.CONFIG = config
        self.OBSIDIAN_CONFIG = self.load_obsidian_config(config)

    def load_obsidian_config(self, CONFIG):
        with open(CONFIG["obsidian-config-path"], "r") as file:
            return json.loads(file.read())

    def get_all_vaults(self):
        vaults = []
        for v in self.OBSIDIAN_CONFIG["vaults"]:
            vaults.append(Vault(v, self.OBSIDIAN_CONFIG["vaults"][v]))
        return vaults

    def hash_file(self, file_path, hasher=hashlib.sha512, hex=False):
        # Calculate the hash of a file.
        with open(file_path, 'rb') as f:
            file_hash = hasher()
            while chunk := f.read(4096):
                file_hash.update(chunk)
        return file_hash.hexdigest() if hex else file_hash.digest()

    def hash_folder(self, folder_path, hasher=hashlib.sha512):
        # Calculate the hash of a folder.
        folder_hash = hasher()
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_hash = hash_file(file_path, hasher=hasher)
                folder_hash.update(file_hash)
        return folder_hash.hexdigest()

    def hash_path(self, path):
        if os.path.isfile(path):
            return hash_file(path, hex=True)
        else:
            return hash_folder(path)

    # check derivation of current state of master_vault to last time checked (is updating needed?)
    def check_derivation(self, master_vault : Vault):
        sync_needed = []
        for item in self.CONFIG["settings"]["sync"]:
            if item not in self.CONFIG["settings"]["vault-config-hashes"].keys():
                sync_needed.append(item)
                sha = hash_path(os.path.join(master_vault.path, item))
                self.CONFIG["settings"]["vault-config-hashes"][item] = sha
                print(f"Added hash for {item}")
            else:
                cur_sha = hash_path(os.path.join(master_vault.path, item))
                if cur_sha != self.CONFIG["settings"]["vault-config-hashes"][item]:
                    sync_needed.append(item)
                    self.CONFIG["settings"]["vault-config-hashes"][item] = cur_sha
                    print(f"Updated hash for {item}")

    def sync_all_vaults(self):
        pass

    def get_vault_by_id(self, id):
        vaults = self.get_all_vaults()
        vault = list(filter(lambda vault: vault.id == id, vaults))
        if len(vault) == 1:
            return vault[0]
        else:
            return None

    def get_master_vault(self):
        return self.get_vault_by_id(self.CONFIG["settings"]["master-vault"])

    def temp(self):
        vaults = get_all_vaults()
        print(f"vaults found: {len(vaults)}")
        master_vault = list(filter(lambda vault: vault.id == self.CONFIG["settings"]["master-vault"], vaults))[0]
        print(f"master-vault: {master_vault}")
        check_derivation(master_vault) 
