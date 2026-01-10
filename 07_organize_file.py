import os

folder_path = 'test_folder' 

files = os.listdir(folder_path)
data = {}
file_type = {
    "images": [".jpg", ".png", ".jpeg", ".gif"],
    "videos": [".mp4", ".mkv"],
    "musics": [".mp3", ".wav"],
    "zip": [".zip", ".tgz", ".rar", ".tar"],
    "documents": [".pdf", ".docx", ".csv", ".xlsx", ".pptx", ".doc", ".ppt", ".xls"],
    "setup": [".msi", ".exe"],
    "programs": [".py", ".c", ".cpp", ".php"],
    "design": [".xd", ".psd"]
    }


print(f"Files in '{folder_path}':")

for file in files:
    full_path = os.path.join(folder_path, file)

    if os.path.isfile(full_path):
        lower_file = file.lower()
        data[file] = lower_file

for original_file, lower_file in data.items():
    extension = os.path.splitext(lower_file)

    if extension in file_type:
        category = file_type[extension]
    else:
        category = "Others"

    print(f"{original_file} → {category}")

print(data)