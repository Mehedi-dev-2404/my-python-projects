#this is a countdown timer project
#I will make a timer which will countdown to the time we input
#after the input is done we diplay times up

import time
time_sec = 0
while time_sec > 0:
    try:
        time_sec = int(input("Input time in seconds: "))
        if time_sec < 0:
            print("The number cannot be negative")
    except ValueError:     
        print("Not an integer.")

for i in range(time_sec, 0 , -1):
    print(f"⏳ {i} seconds left")
    time.sleep(1)