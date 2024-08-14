#!/bin/bash

# Check if a folder path argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <folder_path>"
  exit 1
fi

# Maximum size of each zip file in MB
max_size=1950m
# Output path for the zip files
output_path="/tmp/crew-chief-autovoicepack/"

# Convert max_size to bytes for arithmetic comparison
max_size_bytes=$((1950 * 1024 * 1024))

# Get the full folder path and extract the folder name
dir="$1"

# input_folder is the base folder for this voice created by generate_voice_pack.py
# such as "output/Luis"
input_folder=$(basename "$dir")

# Check if the provided directory exists
if [ ! -d "$dir" ]; then
  echo "Error: Directory $dir does not exist."
  exit 1
fi

# Create zip file output dir
echo "Creating output directory at $output_path..."
mkdir -p "$output_path"

counter=1
current_size=0
last_dir=""

echo "Processing folder: $input_folder"

echo "Removing existing zip files for $input_folder..."
rm -f "$output_path/crew-chief-autovoicepack-$input_folder-*.zip"

# Find and loop over each file in the specified subdirectory, recursively
echo "Creating CrewChief voice pack zip file for $input_folder at $output_path..."
find "$dir" -type f | while read -r file; do
  file_size=$(du -b "$file" | cut -f1)
  current_dir=$(dirname "$file")

  # Check if the directory has changed
  if [ "$current_dir" != "$last_dir" ]; then
    echo "  $current_dir"
    last_dir="$current_dir"
  fi

  # Check if adding this file would exceed the max_size
  if [ $((current_size + file_size)) -ge $max_size_bytes ]; then
    # If it exceeds, start a new zip archive
    echo "  Creating new zip file: crew-chief-autovoicepack-$input_folder-${counter}.zip"
    counter=$((counter + 1))
    current_size=0
  fi

  # Add file to the current zip archive
  zip -1 -r -q "$output_path/crew-chief-autovoicepack-$input_folder-${counter}.zip" "$file"

  # Update current size
  current_size=$((current_size + file_size))
done

echo "Finished processing folder: $input_folder"
