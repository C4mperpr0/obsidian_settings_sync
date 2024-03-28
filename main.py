import json
import os
from obsidianSettingsSync import ObsidianSettingsSync
import argparse
import copy

__version__ = "Version 1.1.0 of ObsidianSettingsSync by Carl Heinrich Bellgardt"

def main():
  ### parse arguments

  # create argument parser
  parser = argparse.ArgumentParser(description='Command line tool to sync obsidian settings and plugins between vaults because somehow obsidian still can\'t do this on it\'s own like it\' 1984.')

  # arguments and flags
  parser.add_argument('--list-vaults', '-l', action='store_true', help='List all vault registered in obsidian config file.')
  parser.add_argument('--list-synced', '-s', action='store_true', help='List all files and folders that are synced between vaults.')
  parser.add_argument('--add-synced', '-a', action='store', help='Add item to sync list.')
  parser.add_argument('--remove-synced', '-r', action='store', help='Remove item from sync list.')
  parser.add_argument('--master', '-m', action='store_true', help='Print current vault declared as master vault.')
  parser.add_argument('--set-master', '-M', action='store', help='Set new master by it\'s ID.')
  parser.add_argument('--set-conf', '-C', action="store", help='Set configuration variable with syntax \"var=value\".')
  parser.add_argument('--list-conf', '-c', action="store_true", help='List all configuration variables.')
  parser.add_argument('--version', '-v', action="version", version=__version__, help='Show current version of this very tool.')
  

  # parse args
  args = parser.parse_args()

  ### initialize
  def load_config():
    if os.path.exists("config.json"):
      with open("config.json", "r") as file:
        return json.loads(file.read())
    else:
      print("no config found!")

  def save_config(config):
    with open("config.json", "w+") as file:
      file.write(json.dumps(config, indent=4))

  INIT_CONFIG = load_config()
  OSS = ObsidianSettingsSync(copy.deepcopy(INIT_CONFIG))

  ### apply args

  # list-values
  if args.list_vaults:
    for vault in OSS.get_all_vaults():
      print(f"{vault} {'<master>' if OSS.CONFIG['settings']['master-vault'] == vault.id else ''}")

  # list-synced
  elif args.list_synced:
    for synced in OSS.CONFIG["settings"]["sync"]:
      print(synced)

  # add-synced
  elif args.add_synced:
    if args.add_synced not in OSS.CONFIG["settings"]["sync"]:
      OSS.CONFIG["settings"]["sync"].append(args.add_synced)
      print(f"Added to sync list: {args.add_synced}")
    else:
      print(f"Already syncing: {args.add_synced}")

  # remove-synced
  elif args.remove_synced:
    if args.remove_synced in OSS.CONFIG["settings"]["sync"]:
      OSS.CONFIG["settings"]["sync"].remove(args.remove_synced)
      OSS.CONFIG["settings"]["vault-config-hashes"].pop(args.remove_synced)
      print(f"Removed from sync list: {args.remove_synced}")
    else:
      print(f"Was not in sync list: {args.remove_synced}")

  # list-conf
  elif args.list_conf:
    print(f'full_check={OSS.CONFIG["settings"]["full-check"]} # will compare all synced files and not just copy over derivates of master')
    print(f'master_vault={OSS.CONFIG["settings"]["master-vault"]} # vault from which files will be sync to all other vaults')
    print(f'auto_open_vault={OSS.CONFIG["settings"]["auto-open-vault"]} # automatically open vault 5s after startup of this program')
    print(f'obsidian_config_path={OSS.CONFIG["obsidian-config-path"]} # where your obsidian.json is located')

  # set-conf
  elif args.set_conf:
    var, val = args.set_conf.split("=")
    if var == "full_check":
      OSS.CONFIG["settings"]["full-check"] = val == "True"
    elif var == "master_vault":
      OSS.CONFIG["settings"]["master-vault"] = str(val)
    elif var == "auto_open_vault":
      OSS.CONFIG["settings"]["auto-open-vault"] = val == "True"
    elif var == "obsidian_config_path":
      OSS.CONFIG["obsidian-config-path"] = str(val)
    else:
      print(f"Could not find var named \"{var}\"")

  # master
  elif args.master:
    print(f"{OSS.get_master_vault()} <master>")

  # set-master
  elif args.set_master:
    OSS.CONFIG["settings"]["master-vault"] = args.set_master
    print(f"New master will be: {OSS.get_master_vault()}")

  # none
  else:
    master_drvs = OSS.check_derivation(OSS.get_master_vault())
    OSS.sync_all_vaults(master_drvs, full_check=OSS.CONFIG["settings"]["full-check"])

  # update tool config
  if INIT_CONFIG != OSS.CONFIG:
    save_config(OSS.CONFIG)
  quit()

if __name__ == '__main__':
    main()