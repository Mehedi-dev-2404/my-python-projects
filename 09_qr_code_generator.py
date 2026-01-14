import qrcode

data = "https://google.com"
img = qrcode.make(data)
img.save("qr.png")

print("QR code generated successfully")