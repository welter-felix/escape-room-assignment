# The engine connects the rooms, command handlers, player state, and transcript.
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

def start_game(start_room,data,transcript_filename):
    # Create each room and index it by lowercase name for case-insensitive lookup.
    # Pass the selected data folder to rooms that read evidence files.
    rooms = {room.name.lower(): room for room in [IntroRoom(), VaultRoom(data), DnsRoom(data), SocRoom(data), MalwareRoom(data), FinalGateRoom(data)]}

    # Use the intro room as a safe starting point if the requested room does not exist.
    start_room = start_room.lower()
    if start_room not in rooms:
        print(f"[Game] Unknown start room \"{start_room}\", starting in intro instead.")
        start_room = "intro"

    # Keep track of the player's current room and progress throughout the game.
    state = GameState(current_room=start_room)

    print ("[Game] Cyber Escape Room started. Type 'help' for commands.")
    # Display the starting room before asking the player for a command.
    for line in COMMANDS["look"](state, rooms, None):
        print(line)

    # Read commands until the player quits or closes/interrupts the input.
    try:
        while True:
            # Split the typed line, then find the matching command handler.
            cmd, arg = parse_command(input("> "))
            handler = COMMANDS.get(cmd)

            # Give an error for unknown commands; otherwise run the selected handler.
            if handler is None:
                lines = ["Unrecognised command. Type \"help\" to learn more"]
            else:
                lines = handler(state, rooms, arg)

            # Handlers return display lines; the engine is responsible for printing them.
            for line in lines:
                print(line)

            # Stop the command loop after displaying the quit message.
            if cmd == "quit":
                break

    # Even if input is interrupted, continue so the transcript can be written below.
    except (KeyboardInterrupt, EOFError):
        print()

    # Write the final transcript after the game ends.
    write_transcript(state, transcript_filename)
    print(f"[Game] Transcript written to {transcript_filename}")
                