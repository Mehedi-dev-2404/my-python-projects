import random
print("WELCOME TO THE LEGENDARY ROCK SCISSORS AND PAPER GAME")

player_input = 0
game_counter = 0

while player_input != "Q":
    if player_input == "ROCK" or "SCISSORS" or "PAPER":
        player_input = input("Give your choice: (Rock, Paper, Scissors): ").upper()
        bot_list = ["ROCK", "SCISSORS", "PAPER"]
        game_counter += 1
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
        print(f"This is your {game_counter} game")
    else: print("INVALID INPUT! Plese enter one of (Rock, Paper, Scissors)")         