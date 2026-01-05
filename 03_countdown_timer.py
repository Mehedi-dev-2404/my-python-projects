#this is a countdown timer project
#I will make a timer which will countdown to the time we input
#after the input is done we diplay times up

import time
time_sec = int(input("Input time in seconds: "))

for i in range(time_sec + 1):
    print(i)
    time.sleep(1)