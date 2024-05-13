import threading
from hangman import GameState
from utils import clear, print_hangman_title, print_menu, init_revealed_word
from httpClientServer import * 

def main():
    clear()
    # Init & game title
    print_hangman_title()
    print("======================================================")
    print_menu()
    choice = int(input("> your choice : "))
    player_name = input("> Enter your username : ")

    if choice == 1 :
        player_details = PlayerDetails(
            player_name=player_name,
            is_guesser=False
        )
        game_state = GameState(
            player_details=player_details,
            is_role=IS_HOST
        )
        shared_data = {
            'game_state': game_state
        }
        server(shared_data)

    elif choice == 2 :
        ip = input("> Enter host ip (without xxxx://) : ")
        if ip == "" :
            ip = "localhost:8000"
        player_details = PlayerDetails(
            player_name=player_name,
            is_guesser=True
        )
        game_state = GameState(
            player_details=player_details,
            is_role=IS_CLIENT
        )
        shared_data = {
            'game_state': game_state,
            'ip': ip
        }
        client(shared_data)

if __name__ == "__main__":
    main()