#this is a countdown timer project
#I will make a timer which will countdown to the time we input
#after the input is done we diplay times up

import time
time_sec = 0

def play():
    while True:
        try:
            time_sec = int(input("Input time in seconds: "))
            if time_sec < 0:
                print("The number cannot be negative")
                continue
            if time_sec == 0:
                print("The number cannot be zero")
                continue
        except ValueError:
            print("Not an integer.")
            continue

        for i in range(time_sec, 0 , -1):
                minutes = i // 60
                seconds = i % 60
                print(f"⏳ {minutes:02}:{seconds:02}")
                time.sleep(1)
        break

play()