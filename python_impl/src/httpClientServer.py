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
from hangman import Hangman, PlayerDetails

connection_pool = []


def client(shared_data) :
    ip = shared_data['ip']
    async def handler():
        async with websockets.connect('ws://'+ip) as websocket:
            client_game_state = shared_data['game_state']
            is_connected = False
            continue_game = True
            Hangman_game = Hangman(client_game_state, websocket)
            # Connection Loop
            while continue_game:
                if not is_connected :
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "SYN"
                        }
                    ))
                    syn_ack_response = await websocket.recv()
                    syn_ack_response = json.loads(syn_ack_response)
                    host_details = json.loads(syn_ack_response["player_details"])
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "ACK", 
                            "player_details": json.dumps(client_game_state.player_details.get_player_details_dic())
                        }
                    )) # Connection established
                    is_connected = True
                    print(">> Successfuly connected !")
                    # set him as the guesser in this game instance
                    if client_game_state.player_details.is_guesser :
                        Hangman_game.set_guesser(client_game_state.player_details)
                    else :
                        Hangman_game.set_guesser(host_details)
                else:
                    # Init the game_state
                    await Hangman_game.init_game()

                    # Game Loop : 
                    await Hangman_game.game_loop()

                    # Rematch request if you are a guesser
                    continue_game = await Hangman_game.rematch()
 
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(handler())

def server(shared_data): 
    async def handler(websocket, path):
        server_game_state = shared_data['game_state']
        continue_game = True
        Hangman_game = Hangman(server_game_state, websocket)
        while continue_game:
            # Do handshake :
            if len(connection_pool) == 0 :
                # pre-process incomming data 
                raw_data = await websocket.recv()
                data_dic = json.loads(raw_data)
                if data_dic['HDSHK'] == "SYN":
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "SYN-ACK",
                            "player_details": json.dumps(server_game_state.player_details.get_player_details_dic())
                        }
                    )) 
                    handshake_response = await websocket.recv()
                    handshake_response = json.loads(handshake_response)
                    if handshake_response['HDSHK'] == "ACK":
                        print(">> successfully connected !")
                        # Get player details :
                        guesser_details = PlayerDetails()
                        guesser_details.set_player_details_from_dic(
                            json.loads(handshake_response['player_details'])
                        )
                        connection_pool.append(guesser_details)
                        # set him as the guesser in this game instance
                        if guesser_details.is_guesser :
                            Hangman_game.set_guesser(guesser_details)
                        else :
                            Hangman_game.set_guesser(server_game_state.guesser)
                        continue
            else :
                await Hangman_game.init_game()

                # Game Loop : 
                await Hangman_game.game_loop()

                # Rematch request if you are a guesser
                continue_game = await Hangman_game.rematch()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handler, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("> From the ngrok process, share the adress with your friend without the xxx://")
    print("> Waiting for players ...")
    asyncio.get_event_loop().run_forever() # on each hit of the ws, the handler() is going to get called (psspss)
  
