#!/usr/bin/env python

import json
import os
from obsidianSettingsSync import ObsidianSettingsSync
import argparse
import copy
import config
import subprocess

__version__ = "Version 3.0.1 of ObsidianSettingsSync by Carl Heinrich Bellgardt"

def main():
  ### parse arguments

  # create argument parser
  parser = argparse.ArgumentParser(description='Command line tool to sync obsidian settings and plugins between vaults because somehow obsidian still can\'t do this on it\'s own like it\'s 1984.')

  # arguments and flags
  parser.add_argument('--init', '-i', action='store_true', help='Start the setup procedure of this program. Will automatically be started at first run or if config is not found or corrupt.')
  parser.add_argument('--open-folder', '-o', action='store', help='Open path as obsidian vault.')
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

    print("\n\nThis tool should now be fully set up. If everything worked, you can now run this tool to open obsidian instead of using obsidian directly. ONLY THEN this tool can (every time you run it) search for new vaults to sync to and run the versioning (if enabled). If you want to re-run this setup again, run \"obsidiansettingssync --init\". For more information on how to change settings or use this tool, run \"obsidiansettingssync --help\". \n << Obsidian Settings Sync by Carl Heinrich Bellgardt >> ")
    config.save_config(OSS.CONFIG)
    quit()

  ### apply args (exept -i/--init)

  OSS = ObsidianSettingsSync(copy.deepcopy(INIT_CONFIG))

  # list-conf
  if args.open_folder:
    path = args.open_folder
    print(path)
    # convert local path to absolute path
    if path.startswith("."):
      path = os.path.join(os.getcwd(), path)
    elif not path.startswith("/"):
      path = os.path.join(os.getcwd(), path)
    path = path.replace('./', '')
    conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"vault_cache/{vault_hash}")
    master_conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), vault_cache/master_config)
    
    if not os.path.exists(path):  
      # check if path is correct
      print("\"{path}\" does not exist!")
      exit()
    elif not os.path.isdir(path):
      print("\"{path}\" is not a folder!")
      exit()

    elif path in OSS.CONFIG["synced-vaults"]:
      # make obsidian open that vault
      pass
    elif os.path.exists(os.path.join(path, ".obsidian/")):
      print("Vault already has .obsidian folder, that is not synced. Remove it, if you don't need it's configs and run this again.")
      exit()
    else:
      # setup new synced config
      vault_hash = ObsidianSettingsSync.hash_string(path)
      OSS.CONFIG["synced-vaults"][path] = vault_hash
      config.save_config(OSS.CONFIG)

      # create and link new .obsidian folder
      os.mkdir(f"./vault_cache/{vault_hash}")
      ObsidianSettingsSync.create_simlink(confpath, os.path.join(path, ".obsidian/"))

      # sync everything
      for sync in OSS.CONFIG["settings"]["sync"]:
        sync_src = os.path.join(master_conf_path, sync)
        sync_dst = os.path.join(conf_path, sync)
        # create path to sync if it does not exist
        if not os.path.exists(sync_src):
          if sync_src.endswith("/"):
            # create dir
            os.mkdir(sync_src)
          else:
            # touch file
            with open(sync_src, 'a'):
              os.utime(sync_src, None)
        # sync path
        ObsidianSettingsSync.create_simlink(sync_src, sync_dst)

  elif args.test:
    master_conf_path = "/home/carl/Documents/git/obsidian_settings_sync/v3/src/vault_cache/master_config"
    conf_path = "/home/carl/Documents/git/obsidian_settings_sync/v3/src/vault_cache/a92c9790d3799212ee7c5c4bc3f0749a5aab99dd55dabefdbc3242f48bcd69a8280d48a2b10e946b75460a7ef0eb514f4f2059a84ca8309a1a8f81c45bd49fcb"
    




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