import qrcode
import os

data = input("Enter the data to encode: ")
file_name = input("Enter the name of the file: ")

output_file = f"{file_name}.png"

if os.path.exists(file_name):
    print(f"Stop '{file_name}' already exists. I won't overwrite it.")
else:
    img = qrcode.make(data)
    img.save(f"{output_file}.png")

print("QR code generated successfully")
print(f"File address: /Users/mehedimostafa/Desktop/PROJECTS/New Projectxx/my-python-projects/{file_name}.png")