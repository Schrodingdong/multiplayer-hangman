from utils import *

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
        print("Word :", format_revealed_word(revealed_word))
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