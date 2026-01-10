import os

folder_path = 'test_folder' # Replace with your folder name

# Get a list of every file and folder inside
files = os.listdir(folder_path)

print(f"Files in '{folder_path}':")
for file in files:
    print(file)