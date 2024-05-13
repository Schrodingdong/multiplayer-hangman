import os

MAX_TRIES = 6
FORBIDDEN_CHARS = [' ', '\n']

# IDs to identify the guesser
HOST_ID = "HOST"
PLAYER_ID = "PLAYER"

def clear():
    try:
        os.system('cls')
    except:
        os.system('clear')

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
    print(hangman_stages.get(step, "Invalid step"))
    return hangman_stages.get(step, "Invalid step")

def print_win_screen(playername, has_won):
    print("\n\n========================================================")
    if has_won:
        print(f"{playername} won :D !")
    else:
        print(f"{playername} lost :((")
    print("========================================================")


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