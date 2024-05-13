import threading
import hangman
from utils import clear, print_hangman_title, print_menu, init_revealed_word
from httpClientServer import * 



class GameState:
    def __init__(self, player_name="anon", word_to_guess = "word") -> None:
        self.player_name = player_name
        self.tries = 0
        self.word_to_guess = word_to_guess 
        self.revealed_word = init_revealed_word(self.word_to_guess)
        self.revealed_chars = []
        self.guesser = PLAYER_ID

    def set_player_name(self, player_name):
        self.player_name = player_name

    def swap_guesser(self):
        if self.guesser == HOST_ID :
            self.guesser = PLAYER_ID
        elif self.guesser == PLAYER_ID :
            self.guesser = HOST_ID
    
    
    def set_word_to_guess(self, word_to_guess): 
        self.word_to_guess = word_to_guess 
        self.revealed_word = init_revealed_word(self.word_to_guess)
    
    def copy_game_state(self, game_state_dic):
        self.tries          = game_state_dic['tries']
        self.word_to_guess  = game_state_dic['word_to_guess']
        self.revealed_word  = game_state_dic['revealed_word']
        self.revealed_chars = game_state_dic['revealed_chars']

    def reset_game_state(self, word_to_guess):
        self.tries = 0
        self.set_word_to_guess(word_to_guess)
        self.revealed_chars = []


    def get_game_state_dic(self):
        return {
            "player_name"   : self.player_name,
            "tries"         : self.tries,
            "word_to_guess" : self.word_to_guess,
            "revealed_word" : self.revealed_word,
            "revealed_chars": self.revealed_chars
        }

    

# This object will be used as a template to layer on top of the current game state.
# The current game state will be either generated from the host, or distant player.
# It is also a global object because we want to use it in the threads
game_state = GameState()




def main():
    clear()
    # Init & game title
    print_hangman_title()
    print("======================================================")
    print_menu()
    choice = int(input("> your choice : "))
    player_name = input("> Enter your username : ")
    game_state.set_player_name(player_name)



    if choice == 1 :
        shared_data = {
            'game_state': game_state
        }
        server(shared_data)
    elif choice == 2 :
        ip = input("> Enter host ip (without xxxx://) : ")
        shared_data = {
            'game_state': game_state,
            'ip': ip
        }
        client(shared_data)

if __name__ == "__main__":
    main()