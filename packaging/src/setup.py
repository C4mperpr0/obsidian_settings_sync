#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='obsidian-settings-sync',
      version='1.2.5',
      # Modules to import from other scripts:
      packages=find_packages(),
      # Executables
      scripts=["main.py"],
     ) 
