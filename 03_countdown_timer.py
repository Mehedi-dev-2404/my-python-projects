#this is a countdown timer project
#I will make a timer which will countdown to the time we input
#after the input is done we diplay times up

import time
time_sec = 0

def play():
    while True:
        bar_length = 20
        try:
            time_sec = int(input("Input time in seconds: "))
            total_time = time_sec
            if time_sec < 0:
                print("The number cannot be negative")
                continue
            if time_sec == 0:
                print("The number cannot be zero")
                continue
        except ValueError:
            print("Not an integer.")
            continue

        for i in range(time_sec, -1 , -1):
                filled_block = int((i / total_time) * bar_length)
                minutes = i // 60
                seconds = i % 60
                print(f"⏳ {minutes:02}:{seconds:02} | " + "█" * (bar_length - filled_block) + "░" * filled_block) 
                time.sleep(1)
        break
    print("⏰ Time’s up!")
play()