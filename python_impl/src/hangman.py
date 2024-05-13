from utils import *
import asyncio
import websockets
import json

class PlayerDetails:
    def __init__(self, player_name = "", is_guesser = None) -> None:
        self.player_name = player_name
        self.is_guesser = is_guesser
    
    def get_player_details_dic(self):
        return {
            "player_name": self.player_name,
            "is_guesser": self.is_guesser
        }
    
    def set_player_details_from_dic(self, player_details):
        if not isinstance(player_details, dict) :
            player_details = player_details.get_player_details_dic()
        self.player_name = player_details['player_name']
        self.is_guesser = player_details['is_guesser']
    
    def set_as_guesser(self):
        self.is_guesser = True
    def unset_as_guesser(self):
        self.is_guesser = True
    
    def to_string(self):
        return self.get_player_details_dic()

class GameState:
    def __init__(self, player_details = None, word_to_guess = "word", is_role="") -> None:
        if player_details == None:
            raise Exception("Player detail should be provided")
        self.player_details = player_details
        self.tries = 0
        self.word_to_guess = word_to_guess 
        self.revealed_word = init_revealed_word(self.word_to_guess)
        self.revealed_chars = []
        self.guesser = PlayerDetails()
        # self.guesser = PLAYER_ID
        # self.guesser_name = "John Doe"
        if is_role == IS_CLIENT :
            self.is_client = True
            self.is_host = False
        elif is_role == IS_HOST :
            self.is_host = True
            self.is_client = False
        else :
            raise Exception("is_role param needs to be specified : IS_CLIENT or IS_HOST")
    

    # def swap_guesser(self):
    #     if self.guesser == HOST_ID :
    #         self.guesser = PLAYER_ID
    #     elif self.guesser == PLAYER_ID :
    #         self.guesser = HOST_ID
    def set_guesser(self, guesser_details):
        self.guesser.set_player_details_from_dic(guesser_details)
    
    
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
            "player_details"   : self.player_details.get_player_details_dic(),
            "tries"         : self.tries,
            "word_to_guess" : self.word_to_guess,
            "revealed_word" : self.revealed_word,
            "revealed_chars": self.revealed_chars
        }
    


class Hangman:
    def __init__(self, game_state, websocket) -> None:
        self.game_state = game_state
        self.websocket = websocket
    
    def set_guesser(self, guesser_details):
        self.game_state.set_guesser(guesser_details.get_player_details_dic())
    
    async def init_game(self):
        websocket = self.websocket
        # Init the game_state
        if self.game_state.guesser.player_name == self.game_state.player_details.player_name:
            # Wait for receiving the gamestate
            game_state_init = await websocket.recv()
            self.game_state.copy_game_state(json.loads(
                json.loads(game_state_init)["game_state"]
            ))
        else :
            # define the word
            word_to_guess = input("> Enter the word to guess : ")
            self.game_state.reset_game_state(word_to_guess)
            # send the game state
            await websocket.send(json.dumps(
                {
                    "game_state": json.dumps(self.game_state.get_game_state_dic())
                }
            )) 


    async def game_loop(self):
        websocket = self.websocket
        error = ""
        # Game Loop : 
        print(self.game_state)
        while self.game_state.tries < MAX_TRIES and self.game_state.revealed_word != self.game_state.word_to_guess:
            # Be the one to guess
            if self.game_state.guesser.player_name == self.game_state.player_details.player_name:
                # print the layout
                clear()
                print_hanged_man(self.game_state.tries)
                print("Word :", format_revealed_word(self.game_state.revealed_word))
                if error != "" :
                    print(error)
                    error = ""

                # get the guessed char
                guess = input("What is your guess ? (guesses remaining : {})\n-> ".format(MAX_TRIES - self.game_state.tries))

                # Verify input
                is_input_valid,error = check_input(guess, FORBIDDEN_CHARS, self.game_state.revealed_chars)
                # update game state
                if is_input_valid :
                    # Always get the first element
                    guess = process_input(guess)
                    # match with the word to guess
                    did_reveal = False
                    updated_revealed_word, did_reveal = reveal_char_in_word(guess, self.game_state.word_to_guess, self.game_state.revealed_word)
                    self.game_state.revealed_word = updated_revealed_word
                    if not did_reveal:
                        self.game_state.tries += 1
                    else:
                        self.game_state.revealed_chars.append(guess)

                # send game state
                await websocket.send(json.dumps(
                    {
                        "game_state": json.dumps(self.game_state.get_game_state_dic())
                    }
                )) 

                # wait for ack on game state update from server
                game_state_update_response = await websocket.recv()
                game_state_update_response = json.loads(game_state_update_response)
                if game_state_update_response['UPDATE_STATUS'] != "ACK":
                    print("ERROR : problem status issue")
                    return
            else :
                # Be the one to set the word to guess
                if self.game_state.tries >= MAX_TRIES or self.game_state.revealed_word == self.game_state.word_to_guess :
                    break
                # print the layout
                clear()
                print_hanged_man(self.game_state.tries)
                print("Word to guess :", self.game_state.word_to_guess)
                print("Word :", format_revealed_word(self.game_state.revealed_word))

                # wait for the updated game state from the other
                updated_game_state_response = await websocket.recv()
                updated_game_state_response = json.loads(updated_game_state_response)['game_state']
                updated_game_state_response = json.loads(updated_game_state_response)

                # update server local game state
                self.game_state.copy_game_state(
                    updated_game_state_response
                )

                # send ack to update
                await websocket.send(json.dumps(
                    {
                        "UPDATE_STATUS": "ACK"
                    }
                )) 
        has_won = (self.game_state.revealed_word == self.game_state.word_to_guess)
        print_win_screen(self.game_state.guesser.player_name, has_won)
        print("\n")

    async def rematch(self):
        websocket = self.websocket
        # Rematch request if you are a guesser
        if self.game_state.guesser.player_name == self.game_state.player_details.player_name:
            print("Do you wish for a rematch ? y/n")
            rematch = input(">")
            if rematch.lower() == 'n':
                await websocket.send(json.dumps(
                    {
                        "rematch": False,
                        "player_details": self.game_state.player_details.get_player_details_dic()
                    }
                )) 
                return False
            # Send the rematch request to the other 
            await websocket.send(json.dumps(
                {
                    "rematch": True,
                    "player_details": self.game_state.player_details.get_player_details_dic()
                }
            )) 
            # wait for the rematch response
            rematch_response = await websocket.recv()
            rematch_response = json.loads(rematch_response)
            continue_game = rematch_response['rematch']
            player_details = rematch_response['player_details']
            
            if continue_game :
                self.game_state.player_details.unset_as_guesser()
                self.game_state.set_guesser(
                    player_details
                )
                return True
        else :
            print("Waiting for rematch request ...")
            rematch_request = await websocket.recv()
            rematch = json.loads(rematch_request)['rematch']
            player_name = json.loads(rematch_request)['player_details']['player_name']
            if rematch :
                print(f"Player {player_name} requested a rematch !!")
                print("Do you accept ? y/n")
                rematch_response = input("> ")
                if rematch_response.lower() == "y":
                    self.game_state.player_details.set_as_guesser()
                    self.game_state.set_guesser(
                        self.game_state.player_details
                    )
                    await websocket.send(json.dumps(
                        {
                            "rematch": True,
                            "player_details": self.game_state.player_details.get_player_details_dic()
                        }
                    )) 
                else :
                    await websocket.send(json.dumps(
                        {
                            "rematch": False,
                            "player_name": self.game_state.player_details.get_player_details_dic()
                        }
                    )) 
                return True
            else :
                print("no rematch womp womp :/")
                return False