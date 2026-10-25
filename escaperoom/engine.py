#central engine of the game
import time
from escaperoom.commands import parse_command, COMMANDS
from escaperoom.transcript import write_transcript
from escaperoom.rooms.base import GameState
from escaperoom.rooms.intro import IntroRoom
from escaperoom.rooms.vault import VaultRoom
from escaperoom.rooms.dns import DnsRoom
from escaperoom.rooms.soc import SocRoom
from escaperoom.rooms.malware import MalwareRoom
from escaperoom.rooms.finalgate import FinalGateRoom

#Here I think its best to keep track of all our global variables

    
#List of commands we need to implement : look, move <room>, inspect <item>, use <item>, inventory, hint, save, load, quit.


def start_game(start_room,data,transcript_filename):

    #here we put all our rooms in a room dictionary with its name to lowercase to avoid conflicts
    #every room gets the data folder from --data, so it knows where to find its file
    rooms = {room.name.lower(): room for room in [IntroRoom(), VaultRoom(data), DnsRoom(data), SocRoom(data), MalwareRoom(data), FinalGateRoom(data)]}

    #if --start is not a valid room we start in the intro, so the player is always in a real room
    start_room = start_room.lower()
    if start_room not in rooms:
        print(f"[Game] Unknown start room \"{start_room}\", starting in intro instead.")
        start_room = "intro"

    #the state of the current game (room, inventory, tokens)
    state = GameState(current_room=start_room)

    print ("[Game] Cyber Escape Room started. Type 'help' for commands.")
    #show the starting room right away, so the player knows where they are
    for line in COMMANDS["look"](state, rooms, None):
        print(line)
    try:
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
    #Ctrl+C or Ctrl+D also end the game, we still want to write the transcript then
    except (KeyboardInterrupt, EOFError):
        print()

    #the transcript is written once at the end, with the latest result of each room
    write_transcript(state, transcript_filename)
    print(f"[Game] Transcript written to {transcript_filename}")
                