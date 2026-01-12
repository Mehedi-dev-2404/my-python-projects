import requests

url = input("Enter website URL: ")
try:
    response = requests.get(url)
    print("Status code: ", response.status_code)
except:
    print("Website is not reachable")