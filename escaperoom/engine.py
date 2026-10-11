#central engine of the game
import time
from escaperoom.rooms.base import GameState
from escaperoom.rooms.vault import VaultRoom
from escaperoom.rooms.dns import DnsRoom
from escaperoom.rooms.soc import SocRoom
from escaperoom.rooms.malware import MalwareRoom

#Here I think its best to keep track of all our global variables

    
#List of commands we need to implement : look, move <room>, inspect <item>, use <item>, inventory, hint, save, load, quit.


def start_game(start_room,data,transcript_filename):

    #the state of the current game (room, inventory, tokens)
    state = GameState(current_room=start_room)

    #here we put all our rooms in a room dictionary with its name to lowercase to avoid conflicts
    rooms = {room.name.lower(): room for room in [VaultRoom(), DnsRoom(), SocRoom(),MalwareRoom()]}
    file_location = data +"/"
    
    print ("[Game] Cyber Escape Room started. Type 'help' for commands.")
    while True:
        command = input("> ") #gets the user's command
        
        #Make lowercase to make sure there is no errors with capital letters
        command = command.lower()
        #split command into 2 parts in case we get 2
        parts = command.split(maxsplit=1)
        
        #check if we get an argument
        if not parts:
            print("Please provide a command. Type \"help\" to learn more")
            continue
        
        #check if the first argument matches any of our commands
        match(parts[0]):
              
            case "help":
                print("The supported commands are look, move <room>, " \
                            "inspect <item>, use <item>, inventory, hint, save, load, quit")
            case "move":
                #sanity checks to see if the arguments are all correct
                if len(parts) <=1:
                    print("Please provide a room to go to")
                    print("Possible rooms are: " + ", ".join(rooms))
                    continue
                if parts[1] in rooms: #check if it is a valid room in our room dict
                    if state.current_room != parts[1]:
                        state.current_room = parts[1]
                        print("Moving to "+ parts[1])
                        #time.sleep(1) possible sleep timer to make it look cooler
                        #state.current_room.look()   implement look function room
                        
                        
                    else:
                        print("You are already in "+ parts[1])
                else:
                    print("Not a valid room.")
                    print("Possible rooms are: " + ", ".join(rooms))
                    
                    
            case "look":
                #if more than 1 argument throw an error here later TooManyArgumentsError
                if len(parts) >=2:
                    print("Too many arguments. Usage: \"look\"")
                elif state.current_room not in rooms: #this is for removal, only bc we dont have an introroom yet
                    print("Current Room: "+ state.current_room)
                    print("There is nothing here yet. Possible rooms are: " + ", ".join(rooms))
                else:
                    room = rooms[state.current_room]
                    print("Current Room: "+ room.name)
                    print(room.description)
                    if room.items:
                        print("Items here: " + ", ".join(room.items))
                    else:
                        print("There are no items here.")
            case "inspect":
                if len(parts) <=1:
                    print("Please provide an item to inspect. Usage: \"inspect <item>\"")
                    #possible items also showing
                    continue
                #get the room we are in, None if it is not a room object (e.g. "intro") / remove later the None 
                room = rooms.get(state.current_room)
                if room is None or parts[1] not in room.items:
                    print("There is no item called "+ parts[1] + " here. Type \"look\" to see the items.")
                    continue
                #the room solves its puzzle, stores the token in the state and returns the evidence
                result = room.solve(state)
                if result is None:
                    print("Nothing useful was found in "+ parts[1])
                    continue
                print(f"You inspect {parts[1]}...")
                
                # here we print every part of the result from the solve function
                for key, value in result.items():
                    print(f"{key.upper()}={value}")
            case "use":
                pass
            case "inventory":
                if not state.tokens:
                    print("Your inventory is empty.")
                else:
                    print("Tokens collected:")
                    for name, token in state.tokens.items():
                        print(f"  {name}: {token}")
            case "hint":
                pass
            case "save":
                pass
            case "load":
                pass
            case "quit":
                print(f"[Game] Goodbye. Transcript written to {transcript_filename} ")
                break
            case _:
                print("Unrecognised command") #Unrecognised Command Error
                