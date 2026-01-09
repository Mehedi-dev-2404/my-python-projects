import random
with open("words.txt") as box:
    words = box.read().split()
    word = random.choice(words)
    print(word)