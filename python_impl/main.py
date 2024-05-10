import os
import asyncio
import websockets
import hangman
import time
import threading
import json 


def clear():
    os.system('cls')

def print_hangman_title():
    print("""
  _    _                                         
 | |  | |                                        
 | |__| | __ _ _ __   __ _ _ __ ___   __ _ _ __  
 |  __  |/ _` | '_ \ / _` | '_ ` _ \ / _` | '_ \ 
 | |  | | (_| | | | | (_| | | | | | | (_| | | | |
 |_|  |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                      __/ |                      
                     |___/                       
    """)

def print_menu():
    print("\nWelcome to Hangman Game!")
    print("1. Host a Game")
    print("2. Join a Game")
    print("3. Quit")

# =============================================================================================

FORBIDDEN_CHARS = [' ', '\n']

def print_hanged_man(step):
    hangman_stages = {
        0: """
            +---+  
            |   |    
                |    
                |    
                |    
                |    
            =========""",
        1: """
            +---+    
            |   |    
            O   |    
                |    
                |    
                |    
            =========""",
        2: """
            +---+    
            |   |    
            O   |    
            |   |    
                |    
                |    
            =========""",
        3: """
            +---+    
            |   |    
            O   |    
           /|   |    
                |    
                |    
            =========""",
        4: """
            +---+    
            |   |    
            O   |    
           /|\  |    
                |    
                |    
            =========""",
        5: """
            +---+    
            |   |    
            O   |    
           /|\  |    
           /    |    
                |    
            =========""",
        6: """
            +---+    
            |   |    
            O   |    
           /|\  |    
           / \  |    
                |    
            ========="""
    }
    #print(hangman_stages.get(step, "Invalid step"))
    return hangman_stages.get(step, "Invalid step")

def reveal_char_in_word(c, w, revealed_word):
    og_char_iter = iter(w)
    new_revealed_word = ''
    did_reveal = False
    for i in range(len(revealed_word)):
        og_word_char = next(og_char_iter)
        current_revealed_word_char = revealed_word[i]
        if current_revealed_word_char != '_':
            new_revealed_word += current_revealed_word_char
            continue
        else:
            if c == og_word_char:
                new_revealed_word += c
                did_reveal = True
            else:
                new_revealed_word += '_'
    return new_revealed_word, did_reveal

def init_revealed_word(w):
    revealed_word = ''
    for char in w:
        if char == ' ':
            revealed_word += ' '
        else:
            revealed_word += '_'
    return revealed_word

def format_revealed_word(revealed_word):
    formatted_revealed_word = ''
    for char in revealed_word:
        formatted_revealed_word += char + ' '
    return formatted_revealed_word

def check_word_equality(w1, w2):
    if len(w1) != len(w2):
        return False
    for i in range(len(w1)):
        if w1[i] != w2[i]:
            return False
    return True

def process_input(input): 
    return input.strip()[0]

def check_input(guess, forbidden_chars, revealed_chars):
    check_error = ""
    # Take the first character
    try :
        guess = guess.strip()[0]
    except :
        check_error = ">>> Empty guess"
        return False,check_error
    # make sure it's not a forbidden character
    is_forbidden = False
    for forbidden_char in forbidden_chars:
        if guess == forbidden_char:
            check_error = ">>> Forbidden character : '{0}'".format(guess)
            is_forbidden = True
            break
    if is_forbidden:
        return False,check_error

    # make sure it's not already revealed
    is_already_revealed = False
    for revealed_char in revealed_chars:
        if guess == revealed_char:
            check_error = ">>> Character already guessed :'{0}'".format(guess)
            is_already_revealed = True
            break
    if is_already_revealed:
        return False,check_error
    
    return True,check_error

def start_game(event, shared_data) :
    # Start the game only when we are connected
    event.wait()  

    # VARIABLES =========================================
    tries = shared_data['gameState']['tries']
    word_to_guess = shared_data['gameState']['word_to_guess']
    revealed_word = shared_data['gameState']['revealed_word']
    revealed_chars = shared_data['gameState']['revealed_chars']
    error = ""
    # ===================================================

    clear()
    print_hanged_man(tries)
    while tries < MAX_TRIES and not revealed_word == word_to_guess:
        print("Revealed word :", format_revealed_word(revealed_word))
        if error != "" :
            print(error)
            error = ""

        # take input
        print("What is your guess ? (guesses remaining : {})".format(MAX_TRIES - tries))
        guess = input()

        # Verify input
        is_input_valid,error = check_input(guess, FORBIDDEN_CHARS, revealed_chars)
        if is_input_valid :
            # Always get the first element
            guess = process_input(guess)
            # match with the word to guess
            did_reveal = False
            revealed_word, did_reveal = reveal_char_in_word(guess, word_to_guess, revealed_word)
            if not did_reveal:
                tries += 1
            else:
                revealed_chars.append(guess)
        #clear()
        print_hanged_man(tries)

    # win screen :
    print("\n\n========================================================")
    if revealed_word == word_to_guess:
        print("You won :D !")
    else:
        print("You lost :((")
    print("========================================================")





# =============================================================================================

# Constants
MAX_TRIES = 6
FORBIDDEN_CHARS = [' ', '\n']
JOIN = "join"

current_turn = 0 # 0 being the host, 1 being the other

class GameState:
    def __init__(self, player_name, word_to_guess = "") -> None:
        self.player_name = player_name
        self.tries = 0
        self.word_to_guess = word_to_guess if word_to_guess != "" else input("> Enter the word to guess : ") 
        self.revealed_word = init_revealed_word(self.word_to_guess)
        self.revealed_chars = []


def client(event, shared_data) :
    ip = shared_data['ip']
    async def handler():
        is_connected = False
        while True:
            if not is_connected :
                async with websockets.connect('ws://'+ip) as websocket:
                    # establish connection
                    await websocket.send('{"join": "join", "player_name": "hamza"}')
                    # get the response
                    data = await websocket.recv()
                    shared_data = json.loads(data)
                    is_connected = True
            else :
                # do the game
                event.set()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(handler())



def server(event, shared_data): 
    async def handler(websocket, path):
        # Get the data as dic
        data = await websocket.recv()
        data_dic = json.loads(data)

        # check if the player has joined
        if data_dic['join'] == JOIN :
            print(f"player '{data_dic['player_name']}' has joined !")
            await websocket.send(json.dumps(shared_data)) # to send shared data
            event.set() # for starting the game
        
        # The game started
        else :
            gameState = json.loads(data_dic['gameState'])

        
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handler, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("\nWaiting for players ...")
    asyncio.get_event_loop().run_forever()




def main():
    clear()
    print_hangman_title()
    print("======================================================")
    print_menu()
    choice = int(input("> your choice : "))

    player_name = input("\n> Enter your username : ")

    if choice == 1 :
        event = threading.Event()
        # shared_data = {
        #     "gameState": GameState(player_name)
        # }
        word_to_guess = input("> Enter the word to guess : ") 
        global shared_data = {
            "gameState": {
                "player_name" : player_name,
                "tries" : 0,
                "word_to_guess": word_to_guess,
                "revealed_word":  init_revealed_word(word_to_guess),
                "revealed_chars": [],
                "current_turn": 0
            }
        }
        # Start gamee instance
        t1 = threading.Thread(target=start_game, args=(event, shared_data))
        # Start listener
        t2 = threading.Thread(target=server, args=(event, shared_data))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

    elif choice == 2 :
        event = threading.Event()
        #ip = input("> Enter your host ip : ")
        ip = "localhost:8000"
        global shared_data = {
            "gameState": {
                "player_name" : player_name,
            },
            'ip': ip
        }

        # Start gamee instance
        t1 = threading.Thread(target=start_game, args=(event, shared_data))
        # Start listener
        t2 = threading.Thread(target=client, args=(event, shared_data))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

if __name__ == "__main__":
    main()