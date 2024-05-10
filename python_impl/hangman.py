import os

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


def start_game() :
    # VARIABLES =========================================
    MAX_TRIES = 6
    tries = 0
    word_to_guess = "hanae zwina bzaf"
    revealed_word = init_revealed_word(word_to_guess)
    revealed_chars = []
    clear = lambda: os.system('cls')
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
        clear()
        print_hanged_man(tries)

    # win screen :
    print("\n\n========================================================")
    if revealed_word == word_to_guess:
        print("You won :D !")
    else:
        print("You lost :((")
    print("========================================================")

if __name__ == "__main__" :
    start_game()