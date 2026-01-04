import random
print("WELCOME TO THE LEGENDARY ROCK SCISSORS AND PAPER GAME")
print("Type Q to Quit")
player_input = ""

game_counter = 0

while True:
    player_input = input("Give your choice: (Rock, Paper, Scissors): ").upper()

    if player_input == "Q":
        break
    if player_input not in ["ROCK", "SCISSORS", "PAPER"]:
        print("INVALID INPUT! PLEASE ENTER (Rock, Paper, Scissors)")
        continue

    bot_list = ["ROCK", "SCISSORS", "PAPER"]
    game_counter += 1
    bot_input = random.choice(bot_list)

    print(f"Bot chose {bot_input}")
    if player_input == bot_input:
        print("Draw")
    elif player_input == "ROCK":
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
    print(f"This is your {game_counter} game")