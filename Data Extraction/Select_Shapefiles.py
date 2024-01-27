import os
import tqdm

def select_shapefiles(directory, filetype):
    loop = tqdm.tqdm(total=len(os.listdir(directory)))
    for file in os.listdir(directory):
        if not file.endswith(filetype):
            os.remove(os.path.join(directory, file))
        loop.update(1)

def main():
    select_shapefiles("GAGES_shp_files", ".shp")

if __name__ == '__main__':
    main()
    exit(0)