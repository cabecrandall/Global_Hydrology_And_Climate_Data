import os
import zipfile
import re
from tqdm import tqdm

def group_files_by_id(directory):
    # Create a dictionary to group files by their 8-digit ID
    file_groups = {}
    print("Grouping files by ID...");
    loop = tqdm(total=len(os.listdir(directory)));

    # Define a regular expression pattern to extract 8-digit IDs from file names
    id_pattern = re.compile(r'(\d{8})')

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if the file is a regular file
        if os.path.isfile(file_path):
            # Extract the 8-digit ID from the file name
            match = id_pattern.search(filename)
            if match:
                id = match.group(1)
                if id in file_groups:
                    file_groups[id].append(file_path)
                else:
                    file_groups[id] = [file_path]
        loop.update(1)

    return file_groups

def compress_files_by_id(directory, output_directory):
    file_groups = group_files_by_id(directory)
    print("Compressing files...")
    loop = tqdm(total=len(file_groups.items()))


    for id, files in file_groups.items():
        zip_filename = os.path.join(output_directory, f'{id}.zip')
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                zipf.write(file, os.path.basename(file))
        loop.update(1)

if __name__ == '__main__':
    source_directory = 'GAGES_shapefiles'
    output_directory = 'GAGES_shapefiles'

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    compress_files_by_id(source_directory, output_directory)
