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

    def is_vault_synced(self, vault_id):
        if vault_id in self.CONFIG["settings"]["synced-vaults"]:
            return True
        elif vault_id in self.CONFIG["settings"]["blacklisted-vaults"]:
            return False
        elif self.CONFIG["settings"]["sync-new-vaults"]:
            self.CONFIG["settings"]["sync-new-vaults"].append(vault_id)
            return True
        else:
            self.CONFIG["settings"]["blacklisted-vaults"].append(vault_id)
            return False

    def get_all_vaults(self):
        # cache values
        if hasattr(self, "_ALL_VAULTS"):
            return self._ALL_VAULTS

        vaults = []
        for v in self.OBSIDIAN_CONFIG["vaults"]:
            
            vaults.append(Vault(v, self.OBSIDIAN_CONFIG["vaults"][v]))
        self.ALL_VAULTS = vaults
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
                file_hash = self.hash_file(file_path, hasher=hasher)
                folder_hash.update(file_hash)
        return folder_hash.hexdigest()

    def hash_path(self, path):
        if os.path.isfile(path):
            return self.hash_file(path, hex=True)
        else:
            return self.hash_folder(path)

    # check derivation of current state of master_vault to last time checked (is updating needed?)
    # def check_derivation(self, vault : Vault, exempt=[]):
    #     set_config = vault == self.get_master_vault()
    #     sync_needed = []
    #     for item in self.CONFIG["settings"]["sync"]:
    #         if item in exempt:
    #             # if comparing a vault with the master,
    #             # we already now that all derivations within the master itself
    #             # must apply to all slaves
    #             continue
    #         if item not in self.CONFIG["settings"]["vault-config-hashes"].keys():
    #             sync_needed.append(item)
    #             sha = self.hash_path(os.path.join(vault.path, item))
    #             if set_config:
    #                 self.CONFIG["settings"]["vault-config-hashes"][item] = sha
    #             print(f"Added hash for {item}")
    #         else:
    #             cur_sha = self.hash_path(os.path.join(vault.path, item))
    #             if cur_sha != self.CONFIG["settings"]["vault-config-hashes"][item]:
    #                 sync_needed.append(item)
    #                 if set_config:
    #                     self.CONFIG["settings"]["vault-config-hashes"][item] = cur_sha
    #                 print(f"Updated hash for {item}")
    #     return sync_needed

    def copy(self, src, dst):
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy(src, dst)

    # will only copy derivations of master vault to its last check
    # if full_check: will hash vault2 and compare all with master
    # def sync_derivations(self, master_vault : Vault, vault2 : Vault, drvs, full_check=False):
    #     if not full_check:
    #         for drv in drvs:
    #             print(f"syncing {drv} to {vault2.name}")
    #             self.copy(os.path.join(master_vault.path, drv), os.path.join(vault2.path, drv))
    #     else:
    #         # only need to check drvs that are not changed at the master
    #         drvs_to_master = self.check_derivation(vault2, exempt=drvs)
    #         for drv in drvs + drvs_to_master:
    #             print(f"syncing {drv} to {vault2.name}")
    #             self.copy(os.path.join(master_vault.path, drv), os.path.join(vault2.path, drv))  

    def sync_all_vaults(self, master_drvs, full_check=False):
        for vault in self.get_all_vaults():
            if vault.id != self.get_master_vault().id:
                self.sync_derivations(self.get_master_vault(), vault, master_drvs, full_check=full_check)

    def get_vault_by_id(self, id):
        vaults = self.get_all_vaults()
        vault = list(filter(lambda vault: vault.id == id, vaults))
        if len(vault) == 1:
            return vault[0]
        else:
            return None
    
    def sync_vault(self, vault):
        for element in self.CONFIG["settings"]["sync"]:
            src = os.path.join(os.path.dirname(__file__), element)
            dst = os.path.join(vault.path, element)
            if os.path.exists(dst):
                print(f"Cannot create link to \"{dst}\". Path already exists!")
            else:
                self.create_simlink(src, dst)
                print(f"Linked: {src} -> {dst}")

    def create_simlink(self, src, dst):
        # TODO: we also have to make sure that directories DEFINITLY end with a / in the config/settings/sync, otherwise this WILL NOT WORK!!!!!!!!!!!!!!1
        if src.endswith("/"):
            # cur of / at the end, because symlinks work that way
            dst = dst[:-1]
        os.symlink(src, dst)

    # def get_master_vault(self):
    #     # cache value
    #     if hasattr(self, "_MASTER_VAULT"):
    #         return self._MASTER_VAULT

    #     self._MASTER_VAULT = self.get_vault_by_id(self.CONFIG["settings"]["master-vault"])
    #     return self._MASTER_VAULT
