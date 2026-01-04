import random

player_input = input("Give your choice: (Rock, Paper, Scissors): ").capitalize

bot_list = ["ROCK", "SCISSORS", "PAPER"]

bot_input = random.choice(bot_list)

if player_input == bot_input:
    print("Draw")
if player_input == "ROCK":
    if bot_input == "PAPER":
        print("You Lose!")
    elif bot_input == "SCISSORS":
        print("You Win")
elif player_input == "PAPER":
    if bot_input == "SCISSORS":
        print("You Lose!")
    elif bot_input == "ROCK":
        print("You Win")
elif player_input == "SCISSORS":
    if bot_input == "ROCK":
        print("You Lose!")
    elif bot_input == "PAPER":
        print("You Win")
