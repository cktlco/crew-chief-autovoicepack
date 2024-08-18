import os
import sys
import zipfile


# Function to create a zip archive
def create_zip(zip_file_name, files, root_dir, subdir_name):
    with zipfile.ZipFile(zip_file_name, 'a', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            # Modify the archive name to include the subdir
            arcname = os.path.join(subdir_name, os.path.relpath(file, start=root_dir))
            zipf.write(file, arcname)


# Check if a folder path argument is provided
if len(sys.argv) < 2:
    print("Usage: python script.py <folder_path>")
    sys.exit(1)

# Maximum size of each zip file in bytes
max_size_bytes = 2100000000
output_path = "/dev_local/crew-chief-autovoicepack/zip/"

# Get the full folder path and extract the folder name
dir_path = sys.argv[1]
input_folder = os.path.basename(dir_path)

# Check if the provided directory exists
if not os.path.isdir(dir_path):
    print(f"Error: Directory {dir_path} does not exist.")
    sys.exit(1)

# Create the output directory if it doesn't exist
if not os.path.exists(output_path):
    os.makedirs(output_path)

print(f"Processing folder: {input_folder}")

# Remove existing zip files for the input folder
for f in os.listdir(output_path):
    if f.startswith(f"crew-chief-autovoicepack-{input_folder}-") and f.endswith(".zip"):
        os.remove(os.path.join(output_path, f))

# Group files by size
zip_groups = []
current_group = []
current_size = 0

for root, _, files in os.walk(dir_path):
    for file in files:
        file_path = os.path.join(root, file)
        file_size = os.path.getsize(file_path)

        if current_size + file_size > max_size_bytes:
            zip_groups.append((current_group, current_size))
            current_group = []
            current_size = 0

        current_group.append(file_path)
        current_size += file_size

# Add the last group if it has files
if current_group:
    zip_groups.append((current_group, current_size))

# Inform the user how many zip files will be created and their sizes
total_zips = len(zip_groups)
print(f"Total zip files to be created: {total_zips}")
for i, (group, size) in enumerate(zip_groups, 1):
    size_gb = size / (1024 ** 3)
    print(f"  Zip file {i} of {total_zips}: {len(group)} files, uncompressed size {size_gb:.2f} GB")

# Create the zip files
for i, (group, size) in enumerate(zip_groups, 1):
    zip_file_name = os.path.join(output_path, f"crew-chief-autovoicepack-{input_folder}-{i}of{total_zips}.zip")
    size_gb = size / (1024 ** 3)
    print(f"Creating {zip_file_name} with {len(group)} files and uncompressed size {size_gb:.2f} GB...")

    batch_size = 500
    for j in range(0, len(group), batch_size):
        create_zip(zip_file_name, group[j:j + batch_size], root_dir=dir_path, subdir_name=input_folder)

print(f"Finished processing folder: {input_folder}")
