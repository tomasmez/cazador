#!/bin/bash

# Specify the port of your device
PORT="/dev/ttyUSB0"

#if [ -z "$1" ]; then 
#echo "usage: $0 <dir to copy>"
#exit 0
#fi

# Navigate to the directory containing your files
# cd "$1"

# Loop through all files and directories
for item in *; do
    # Check if item is a file
    if [ -f "$item" ]; then
        echo "Copying file: $item"
        ampy --port "$PORT" put "$item"
    fi

    # Check if item is a directory
    if [ -d "$item" ]; then
        echo "Copying directory: $item"
        ampy --port "$PORT" put "$item"
    fi
done

echo "Copy process complete."

