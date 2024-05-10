import threading
import hangman
from utils import clear, print_hangman_title, print_menu, init_revealed_word
from httpClientServer import client, server


current_turn = 0 # 0 being the host, 1 being the other

class GameState:
    def __init__(self, player_name="anon", word_to_guess = "word") -> None:
        self.player_name = player_name
        self.tries = 0
        self.word_to_guess = word_to_guess 
        self.revealed_word = init_revealed_word(self.word_to_guess)
        self.revealed_chars = []

    def set_player_name(self, player_name):
        self.player_name = player_name
    
    def set_word_to_guess(self, word_to_guess): 
        self.word_to_guess = word_to_guess 

    

# This object will be used as a template to layer on top of the current game state.
# The current game state will be either generated from the host, or distant player.
# It is also a global object because we want to use it in the threads
gameState = GameState()




def main():
    clear()
    # Init & game title
    print_hangman_title()
    print("======================================================")
    print_menu()
    choice = int(input("> your choice : "))
    player_name = input("\n> Enter your username : ")

    if choice == 1 :
        event = threading.Event()
        shared_data = {
            "gameState": GameState(player_name)
        }
        word_to_guess = input("> Enter the word to guess : ") 

        # Start gamee instance
        t1 = threading.Thread(target=hangman.start_game, args=(event, shared_data))
        # Start listener
        t2 = threading.Thread(target=server, args=(event, shared_data))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    elif choice == 2 :
        event = threading.Event()
        ip = "localhost:8000"

        # Start gamee instance
        t1 = threading.Thread(target=hangman.start_game, args=(event, shared_data))
        # Start listener
        t2 = threading.Thread(target=client, args=(event, shared_data))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

if __name__ == "__main__":
    main()