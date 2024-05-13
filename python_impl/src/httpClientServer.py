"""
    Things to implement :
    [x] - Handshake from client & server
    [x] - pass game state from one and another
    [x] - use the passed game state as a blueprint to update the current one
    [ ] - make sure to detect the disconnection of the other player and handle it properly
"""
import asyncio
import websockets
import json
from utils import * 

connection_pool = []

class PlayerDetails:
    def __init__(self, player_name = "") -> None:
        self.player_name = player_name
    
    def get_player_details_dic(self):
        return {
            "player_name": self.player_name
        }
    
    def set_player_details(self, player_details):
        self.player_name = player_details['player_name']
    
    def to_string(self):
        return self.get_player_details_dic()

        

def client(shared_data) :
    ip = shared_data['ip']
    async def handler():
        client_game_state = shared_data['game_state']
        async with websockets.connect('ws://'+ip) as websocket:
            is_connected = False
            error = ""
            # Connection Loop
            while True:
                if not is_connected :
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "SYN"
                        }
                    ))
                    syn_ack_response = await websocket.recv()
                    syn_ack_response = json.loads(syn_ack_response)
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "ACK", 
                            "player_details": {
                                "player_name": client_game_state.player_name
                            }
                        }
                    )) # Connection established
                    is_connected = True
                    print(">> Successfuly connected !")
                else:
                    # Init the game_state
                    if client_game_state.guesser == PLAYER_ID:
                        # Wait for receiving the gamestate
                        game_state_init = await websocket.recv()
                        client_game_state.copy_game_state(json.loads(
                            json.loads(game_state_init)["game_state"]
                        ))
                    else :
                        # define the word
                        word_to_guess = input("> Enter the word to guess : ")
                        client_game_state.reset_game_state(word_to_guess)
                        # send the game state
                        await websocket.send(json.dumps(
                            {
                                "game_state": json.dumps(client_game_state.get_game_state_dic())
                            }
                        )) 

                    # Game Loop : 
                    while client_game_state.tries < MAX_TRIES and client_game_state.revealed_word != client_game_state.word_to_guess:
                        # Be the one to guess
                        if client_game_state.guesser == PLAYER_ID  :
                            
                            # print the layout
                            clear()
                            print_hanged_man(client_game_state.tries)
                            print("Word :", format_revealed_word(client_game_state.revealed_word))
                            if error != "" :
                                print(error)
                                error = ""

                            # get the guessed char
                            guess = input("What is your guess ? (guesses remaining : {})\n-> ".format(MAX_TRIES - client_game_state.tries))

                            # Verify input
                            is_input_valid,error = check_input(guess, FORBIDDEN_CHARS, client_game_state.revealed_chars)
                            # update game state
                            if is_input_valid :
                                # Always get the first element
                                guess = process_input(guess)
                                # match with the word to guess
                                did_reveal = False
                                updated_revealed_word, did_reveal = reveal_char_in_word(guess, client_game_state.word_to_guess, client_game_state.revealed_word)
                                client_game_state.revealed_word = updated_revealed_word
                                if not did_reveal:
                                    client_game_state.tries += 1
                                else:
                                    client_game_state.revealed_chars.append(guess)

                            # send game state
                            await websocket.send(json.dumps(
                                {
                                    "game_state": json.dumps(client_game_state.get_game_state_dic())
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
                            if client_game_state.tries >= MAX_TRIES or client_game_state.revealed_word == client_game_state.word_to_guess :
                                break
                            # print the layout
                            clear()
                            print_hanged_man(client_game_state.tries)
                            print("Word :", format_revealed_word(client_game_state.revealed_word))

                            # wait for the updated game state from the other
                            updated_game_state_response = await websocket.recv()
                            updated_game_state_response = json.loads(updated_game_state_response)['game_state']
                            updated_game_state_response = json.loads(updated_game_state_response)

                            # update server local game state
                            client_game_state.copy_game_state(
                                updated_game_state_response
                            )

                            # send ack to update
                            await websocket.send(json.dumps(
                                {
                                    "UPDATE_STATUS": "ACK"
                                }
                            )) 
                
                    # win screen :
                    has_won = client_game_state.revealed_word == client_game_state.word_to_guess
                    print_win_screen(client_game_state.guesser, has_won)
                    print("\n")

                    # Rematch request if you are a guesser
                    if client_game_state.guesser == PLAYER_ID : 
                        print("Do you wish for a rematch ? y/n")
                        rematch = input(">")
                        if rematch.lower() == 'n':
                            await websocket.send(json.dumps(
                                {
                                    "rematch": False,
                                    "player_name": client_game_state.guesser
                                }
                            )) 
                            break
                        # Send the rematch request to the other 
                        await websocket.send(json.dumps(
                            {
                                "rematch": True,
                                "player_name": client_game_state.guesser
                            }
                        )) 
                        # wait for the rematch response
                        rematch_response = await websocket.recv()
                        continue_game = json.loads(rematch_response)['rematch']
                        if continue_game :
                            client_game_state.swap_guesser()
                    else :
                        print("Waiting for rematch request ...")
                        rematch_request = await websocket.recv()
                        rematch = json.loads(rematch_request)['rematch']
                        player_name = json.loads(rematch_request)['player_name']
                        if rematch :
                            print(f"Player {player_name} requested a rematch !!")
                            print("Do you accept ? y/n")
                            rematch_response = input("> ")
                            if rematch_response.lower() == "y":
                                client_game_state.swap_guesser()
                                await websocket.send(json.dumps(
                                    {
                                        "rematch": True,
                                        "player_name": client_game_state.guesser
                                    }
                                )) 
                            else :
                                await websocket.send(json.dumps(
                                    {
                                        "rematch": False,
                                        "player_name": client_game_state.guesser
                                    }
                                )) 
                        else :
                            print("no rematch womp womp :/")
                            break



    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(handler())

def server(shared_data): 
    async def handler(websocket, path):
        server_game_state = shared_data['game_state']
        continue_game = True
        while continue_game:
            # Do handshake :
            if len(connection_pool) == 0 :
                # pre-process incomming data 
                raw_data = await websocket.recv()
                data_dic = json.loads(raw_data)
                if data_dic['HDSHK'] == "SYN":
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "SYN-ACK"
                            #"game_state": json.dumps(server_game_state.get_game_state_dic())
                        }
                    )) 
                    handshake_response = await websocket.recv()
                    handshake_response = json.loads(handshake_response)
                    if handshake_response['HDSHK'] == "ACK":
                        print(">> successfully connected !")
                        # Get player details :
                        player_details = PlayerDetails()
                        player_details.set_player_details(handshake_response['player_details'])
                        connection_pool.append(player_details)
                        continue
            else :
                if server_game_state.guesser == PLAYER_ID :
                    # define the word
                    word_to_guess = input("> Enter the word to guess : ")
                    server_game_state.reset_game_state(word_to_guess)
                    # send the game state
                    await websocket.send(json.dumps(
                        {
                            "game_state": json.dumps(server_game_state.get_game_state_dic())
                        }
                    )) 
                else :
                    # Wait for receiving the gamestate
                    game_state_init = await websocket.recv()
                    server_game_state.copy_game_state(json.loads(
                        json.loads(game_state_init)["game_state"]
                    ))

                # Game Loop : 
                error = ""
                while server_game_state.tries < MAX_TRIES and server_game_state.revealed_word != server_game_state.word_to_guess:
                    if server_game_state.guesser == HOST_ID : # Be the one to guess
                        # print the layout
                        clear()
                        print_hanged_man(server_game_state.tries)
                        print("Word :", format_revealed_word(server_game_state.revealed_word))
                        if error != "" :
                            print(error)
                            error = ""

                        # get the guessed char
                        guess = input("What is your guess ? (guesses remaining : {})\n-> ".format(MAX_TRIES - server_game_state.tries))

                        # Verify input
                        is_input_valid,error = check_input(guess, FORBIDDEN_CHARS, server_game_state.revealed_chars)
                        # update game state
                        if is_input_valid :
                            # Always get the first element
                            guess = process_input(guess)
                            # match with the word to guess
                            did_reveal = False
                            updated_revealed_word, did_reveal = reveal_char_in_word(guess, server_game_state.word_to_guess, server_game_state.revealed_word)
                            server_game_state.revealed_word = updated_revealed_word
                            if not did_reveal:
                                server_game_state.tries += 1
                            else:
                                server_game_state.revealed_chars.append(guess)

                        # send game state
                        await websocket.send(json.dumps(
                            {
                                "game_state": json.dumps(server_game_state.get_game_state_dic())
                            }
                        )) 

                        # wait for ack on game state update from server
                        game_state_update_response = await websocket.recv()
                        game_state_update_response = json.loads(game_state_update_response)
                        if game_state_update_response['UPDATE_STATUS'] != "ACK":
                            print("ERROR : problem status issue")
                            return
                    else : # Be the one to set the word to guess
                        # print the layout
                        clear()
                        print_hanged_man(server_game_state.tries)
                        print("Word to guess :", server_game_state.word_to_guess)
                        print("Revealed word :", format_revealed_word(server_game_state.revealed_word))
                        print(f"\n {server_game_state.guesser} is thinking ...")

                        # wait for the updated game state from the other
                        updated_game_state_response = await websocket.recv()
                        updated_game_state_response = json.loads(updated_game_state_response)['game_state']
                        updated_game_state_response = json.loads(updated_game_state_response)

                        # update server local game state
                        server_game_state.copy_game_state(
                            updated_game_state_response
                        )

                        # send ack to update
                        await websocket.send(json.dumps(
                            {
                                "UPDATE_STATUS": "ACK"
                            }
                        )) 
                # win screen :
                has_won = server_game_state.revealed_word == server_game_state.word_to_guess
                print_win_screen(server_game_state.guesser, has_won)
                print("\n")

                # Rematch request if you are a guesser
                if server_game_state.guesser == HOST_ID : 
                    print("Do you wish for a rematch ? y/n")
                    rematch = input(">")
                    if rematch.lower() == 'n':
                        await websocket.send(json.dumps(
                            {
                                "rematch": False,
                                "player_name": server_game_state.guesser
                            }
                        )) 
                        break
                    # Send the rematch request to the other 
                    await websocket.send(json.dumps(
                        {
                            "rematch": True,
                            "player_name": server_game_state.guesser
                        }
                    )) 
                    # wait for the rematch response
                    rematch_response = await websocket.recv()
                    continue_game = json.loads(rematch_response)['rematch']
                    if continue_game :
                        server_game_state.swap_guesser()
                else :
                    print("Waiting for rematch request ...")
                    rematch_request = await websocket.recv()
                    rematch = json.loads(rematch_request)['rematch']
                    player_name = json.loads(rematch_request)['player_name']
                    if rematch :
                        print(f"Player {player_name} requested a rematch !!")
                        print("Do you accept ? y/n")
                        rematch_response = input("> ")
                        if rematch_response.lower() == "y":
                            server_game_state.swap_guesser()
                            await websocket.send(json.dumps(
                                {
                                    "rematch": True,
                                    "player_name": server_game_state.guesser
                                }
                            )) 
                        else :
                            await websocket.send(json.dumps(
                                {
                                    "rematch": False,
                                    "player_name": server_game_state.guesser
                                }
                            )) 
                    else :
                        print("no rematch womp womp :/")
                        break




    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handler, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("> From the ngrok process, share the adress with your friend without the xxx://")
    print("> Waiting for players ...")
    asyncio.get_event_loop().run_forever() # on each hit of the ws, the handler() is going to get called (psspss)
  
