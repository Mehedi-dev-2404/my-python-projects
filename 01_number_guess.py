# The player will try to guess a randomly generated number between 1 and 100.
# The program will provide feedback on whether the guess is too low, too high, or correct.
# The game continues until the player guesses the correct number.
import random

number = random.randint(1, 100)
attempt = 1
print("Welcome to number guessing game!!")
guess = int(input("Guess a number between (1-100): "))

while guess != number:
    guess = input("Guess a number between (1-100)")
    if guess != number:
        if guess < number:
            print("Incorrect guess, Low")
        elif guess > number:
            print("Incorrect guess, High")
    
    guess = input("Guess a number between (1-100)")
    attempt += 1

print(f"You win! The number was {number}")
print(f"It took you {attempt} attempts.")
