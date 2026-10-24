#central engine of the game
import time
from escaperoom.commands import parse_command, COMMANDS
from escaperoom.rooms.base import GameState
from escaperoom.rooms.vault import VaultRoom
from escaperoom.rooms.dns import DnsRoom
from escaperoom.rooms.soc import SocRoom
from escaperoom.rooms.malware import MalwareRoom
from escaperoom.rooms.finalgate import FinalGateRoom

#Here I think its best to keep track of all our global variables

    
#List of commands we need to implement : look, move <room>, inspect <item>, use <item>, inventory, hint, save, load, quit.


def start_game(start_room,data,transcript_filename):

    #the state of the current game (room, inventory, tokens)
    state = GameState(current_room=start_room)

    #here we put all our rooms in a room dictionary with its name to lowercase to avoid conflicts
    rooms = {room.name.lower(): room for room in [VaultRoom(), DnsRoom(), SocRoom(),MalwareRoom(), FinalGateRoom()]}
    file_location = data +"/"
    
    print ("[Game] Cyber Escape Room started. Type 'help' for commands.")
    while True:
        cmd, arg = parse_command(input("> "))
        handler = COMMANDS.get(cmd)
        if handler is None:
            lines = ["Unrecognised command. Type \"help\" to learn more"]
        else:
            lines = handler(state, rooms, arg)
        for line in lines:
            print(line)
        if cmd == "quit":
            break
                