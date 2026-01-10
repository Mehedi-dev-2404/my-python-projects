import os

folder_path = 'test_folder' 

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

files = os.listdir(folder_path)

for file in files:
    full_path = os.path.join(folder_path, file)

    if not os.path.isfile(full_path):
        continue

    lower_file = file.lower()
    _, extension = os.path.splitext(lower_file)

    category = "Others"
    for folder, extensions in file_type.items():
        if extension in extensions:
            category = folder
            break
    
    category_path = os.path.join(folder_path, category)
    os.makedirs(category_path, exist_ok = True)

    new_path = os.path.join(category_path, file)
    os.rename(full_path, new_path)
    
    print(f"Moved: {file} → {category}/")