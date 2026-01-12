import requests
while True:
    url = input("Enter website URL (or 'exit'): ")
    if url == "exit":
        print("Goodbye")
        break

    if "https://" in url:
        url = url
    else:
        url = "https://" + url

    try:
        response = requests.get(url, timeout=5)
        print("Status code: ", response.status_code)
        if response.status_code == 200:
            print(f"UP {response.status_code}")
        else:
            print("Down (not reachable)")

    except requests.ReadTimeout:
        print("DOWN (Timeout)")

    except requests.ConnectionError:
        print("DOWN (Connection Error)")

    except requests.RequestException:
        print("DOWN (Invalid request)")