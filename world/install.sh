#!/bin/bash
# Script to install Druidia.  
# Requires:
#    Evennia code base is installed.
#    This script is run from base MUD directory (e.g. ~/muddev)

git clone https://github.com/Tiogaplanet/Druidia.git
cd Druidia
evennia migrate && evennia start
