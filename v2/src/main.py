#!/usr/bin/env python

import json
import os
from obsidianSettingsSync import ObsidianSettingsSync
import argparse
import copy
import config
import subprocess

__version__ = "Version 2.0.0 of ObsidianSettingsSync by Carl Heinrich Bellgardt"

def main():
  ### parse arguments

  # create argument parser
  parser = argparse.ArgumentParser(description='Command line tool to sync obsidian settings and plugins between vaults because somehow obsidian still can\'t do this on it\'s own like it\'s 1984.')

  # arguments and flags
  parser.add_argument('--init', '-i', action='store_true', help='Start the setup procedure of this program. Will automatically be started at first run or if config is not found or corrupt.')
  parser.add_argument('--list-vaults', '-l', action='store_true', help='List all vault registered in obsidian config file.')
  parser.add_argument('--sync-vault', '-l', action='store_true', help='Sync vault from now on or check links if vault is already being synced.')
  parser.add_argument('--list-synced', '-s', action='store_true', help='List all files and folders that are synced between vaults.')
  parser.add_argument('--add-synced', '-a', action='store', help='Add item to sync list.')
  parser.add_argument('--remove-synced', '-r', action='store', help='Remove item from sync list.')
  parser.add_argument('--set-conf', '-C', action="store", help='Set configuration variable with syntax \"var=value\".')
  parser.add_argument('--list-conf', '-c', action="store_true", help='List all configuration variables.')
  parser.add_argument('--version', '-v', action="version", version=__version__, help='Show current version of this very tool.')

  parser.add_argument('--test', '-t', action='store_true', help='If you see this option, the dev forgot to take it out!!! Please contact me, this should not be here, since it is only for testing purposes!!!111one')
  

  # parse args
  args = parser.parse_args()

  ### initialize
  INIT_CONFIG = config.load_config()

  # Setup helper
  if INIT_CONFIG is None or args.init:
    print("""
      Welcome to the Obsidian Settings Sync Setup helper!\n The Setup helper is only starting the very first time this program is launched or if it could not detect a valid config.
      If you want to re-run this, just type \"obsidiansettingssync --init\" or type \"obsidiansettingssync --help\" for more information on how to use this tool.
      We now will set everything up together.\n
      """)
    INIT_CONFIG = config.default_config()
    print("\n-------------------- OBSIDIAN CONFIG FILE --------------------")
    print("Where is your obsidian config file (obsidian.json) located? Give the full path! (for example \"/home/exampleuser/.config/obsidian/obsidian.json\")")
    while True:
      path = input(" >> ")
      try:
        with open(path, "r") as file:
          data = json.loads(file.read())
          if "vaults" in data.keys():
            break
          else:
            print("The file is readable, but not containing the key \"vaults\" in it. Please try again!")
      except:
        print("The file cannot be found or is not readable. Please try again!")
    INIT_CONFIG["obsidian-config-path"] = path

    OSS = ObsidianSettingsSync(copy.deepcopy(INIT_CONFIG))
    print("\n-------------------- INITIAL VAULT CONFIG --------------------")
    vaults = OSS.get_all_vaults()
    print(f"Detected {len(vaults)} vaults! You can now select a vault, from which's config you will start, so you don't have to \"start from zero\".")
    print("If you have no vaults at the moment or do not wish to choose no, you can skip this step, and later decide an master-vault via \"obsidiansettingssync --set-master [master_vault_id]\".\n")
    print("[0] - start from zero")
    for i_vault in range(len(vaults)):
      print(f"[{i_vault+1}] - {vaults[i_vault]}")
    while True:
      initial_vault_i = input("\Initial vault config:\n >> ")
      try:
        initial_vault_i = int(mv_i)
      except:
        print("This is not a valid number! Please try again.")
        continue
      if initial_vault_i == 0:
        print("Skipping this step for now...")
        break
      else:
        initial_vault_i -= 1
        if initial_vault_i >= 0 and initial_vault_i < len(vaults):
          print(f"Your initial config will be taken from vault \"{vaults[initial_vault_i].name}\".")
          break
        else:
          print("This number is not an option! Please try again.")

    print("\n-------------------- VERSIONING --------------------")
    print("Do you want to enable versioning? If versioning is enabled, changed to your configs will be committed to a local git repository every time you run this tool. It could be helpful to have basic understanding of git, to actually make use of this in the future. You can use this feature either to roll back your configs in case you messed something up, or to even sync you configs over a remote git repository with other devices.")
    while True:
      versioning = input("[Y/N] >> ")
      if versioning.lower() in ["y", "yes", "yeehaw"]:
        print("Versioning enabled.")
        versioning = True
      elif versioning.lower() in ["n", "no", "no fucking way"]:
        print("Versioning disabled.")
        versioning = False
      else:
        print("Could not understand input. Please use \"Y\" or \"N\".")
        continue
      OSS.CONFIG["settings"]["versioning"] = versioning
      break

    print("\n-------------------- AUTO OPEN VAULT --------------------")
    print("Do you want to automatically run Obsidian every time after running this tool without any arguments (after normal sync)? If disabled, running this tool without any arguments will only sync you settings without opening obsidian afterwards.")
    while True:
      auto_open_vault = input("[Y/N] >> ")
      if auto_open_vault.lower() in ["y", "yes", "yeehaw"]:
        print("Auto-open-vault enabled.")
        auto_open_vault = True
      elif auto_open_vault.lower() in ["n", "no", "no fucking way"]:
        print("Auto-open-vault disabled.")
        auto_open_vault = False
      else:
        print("Could not understand input. Please use \"Y\" or \"N\".")
        continue
      OSS.CONFIG["settings"]["auto-open-vault"] = auto_open_vault
      break

    print("\n\nThis tool should now be fully set up. If everything worked, you can now run this tool to open obsidian instead of using obsidian directly. ONLY THEN this tool can (every time you run it) search for new vaults to sync to and run the versioning (if enabled). If you want to re-run this setup again, run \"obsidiansettingssync --init\". For more information on how to change settings or use this tool, run \"obsidiansettingssync --help\". \n << Obsidian Settings Sync by Carl Heinrich Bellgardt >> ")
    config.save_config(OSS.CONFIG)
    quit()

  ### apply args (exept -i/--init)

  OSS = ObsidianSettingsSync(copy.deepcopy(INIT_CONFIG))

  # list-values
  if args.list_vaults:
    for vault in OSS.get_all_vaults():
      print(vault)

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

  elif args.test:
    vaults = OSS.get_all_vaults()
    OSS.sync_vault(OSS.get_vault_by_id("1ddc9f5b34161d5a"))
    print("synced...")

  # none
  else:
    master_drvs = OSS.check_derivation(OSS.get_master_vault())
    OSS.sync_all_vaults(master_drvs, full_check=OSS.CONFIG["settings"]["full-check"])

  # update tool config
  if INIT_CONFIG != OSS.CONFIG:
    config.save_config(OSS.CONFIG)

  # if OSS.CONFIG["settings"]["auto-open-vault"]:
  #   print("Starting obsidian...")
  #   process = subprocess.Popen(["obsidian"])
  #   return_code = process.wait()
  #   print("Program has exited with return code:", return_code)
  #   print("Syncing again...")
  #   master_drvs = OSS.check_derivation(OSS.get_master_vault())
  #   OSS.sync_all_vaults(master_drvs, full_check=OSS.CONFIG["settings"]["full-check"])
  #   print("Done.")

    # update tool config again (just in case (to be sure))
    if INIT_CONFIG != OSS.CONFIG:
      config.save_config(OSS.CONFIG)

  quit()

if __name__ == '__main__':
    main()