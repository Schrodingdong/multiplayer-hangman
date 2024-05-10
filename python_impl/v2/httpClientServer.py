"""
    Things to implement :
    [x] - Handshake from client & server
    [ ] - pass game state from one and another
    [ ] - use the passed game state as a blueprint to update the current one
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

        

def client(event = None, shared_data= None) :
    ip = shared_data['ip']
    async def handler():
        async with websockets.connect('ws://'+ip) as websocket:
            is_connected = False
            while True:
                if not is_connected :
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "SYN"
                        }
                    ))
                    ack_response = await websocket.recv()
                    ack_response = json.loads(ack_response)
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "ACK", 
                            "player_details": {
                                "player_name": "hamza"
                            }
                        }
                    )) # Connection established
                    is_connected = True
                    print(">> Successfuly connected !")
                else:
                    # print the layout

                    # get the guessed char
                    guessed_char = input("> What is your guess ? ")

                    # process it locally

                    # update game state

                    # send game state

                    # wait for ack on game state update from server


    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(handler())

def server(event = None, shared_data = None): 
    async def handler(websocket, path):
        while True:
            # pre-process incomming data 
            raw_data = await websocket.recv()
            data_dic = json.loads(raw_data)


            # Do handshake :
            if len(connection_pool) >= 0 :
                if data_dic['HDSHK'] == "SYN":
                    await websocket.send(json.dumps(
                        {
                            "HDSHK": "SYN-ACK"
                        }
                    )) 
                    handshake_response = await websocket.recv()
                    handshake_response = json.loads(handshake_response)
                    if handshake_response['HDSHK'] == "ACK":
                        print(">> successfully connected !")
                        # Get player details :
                        player_details = PlayerDetails()
                        player_details.set_player_details(handshake_response['player_details'])
                        print(player_details.to_string())
                        connection_pool.append(player_details)
                        continue
            else :
                print("running game ...")
                # print the layout

                # wait for the updated game state from the other

                # update server local game state

                # send ack to update

    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handler, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("\nWaiting for players ...")
    asyncio.get_event_loop().run_forever() # on each hit of the ws, the handler() is going to get called (psspss)
  
if __name__ == "__main__":
    x = int(input("0: server, 1: client ? "))
    if x == 0 :
        server()
    elif x == 1 :
        client(shared_data={'ip' : 'localhost:8000'})
