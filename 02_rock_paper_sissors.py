import random
print("WELCOME TO THE LEGENDARY ROCK SCISSORS AND PAPER GAME IT IS A BEST OF 3 GAME")
print("Type Q to Quit")
player_input = ""

game_counter = 0
score_player = 0
score_bot = 0
def play():
        global game_counter, score_player, score_bot
        while game_counter != 3:
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
                    score_bot += 1
                elif bot_input == "SCISSORS":
                    print("You Win")
                    score_player += 1

            elif player_input == "PAPER":
                if bot_input == "SCISSORS":
                    print("You Lose!")
                    score_bot += 1
                elif bot_input == "ROCK":
                    print("You Win")
                    score_player += 1
            elif player_input == "SCISSORS":
                if bot_input == "ROCK":
                    print("You Lose!")
                    score_bot += 1
                elif bot_input == "PAPER":
                    print("You Win")
                    score_player += 1
            print(f"This is your {game_counter} game")
            print(f"Your score is {score_player}")
            print(f"Bot score is {score_bot}")
            print()
        if score_bot > score_player:
            print("YOU LOSE! GAME OVER")
        else: print("YOU WIN! GAME OVER")

play()