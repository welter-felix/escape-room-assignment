"""Command handlers for the game.

Each handler receives the game state, room map, and optional command argument,
then returns lines for the engine to display.
"""
from escaperoom.transcript import format_result

import json
from pathlib import Path

# Turn the player's input into a lowercase command name and optional argument.
def parse_command(text):
    # Remove extra spaces, ignore capitalization, and split only at the first space.
    parts = text.strip().lower().split(maxsplit=1)

    # An empty line has no command to dispatch.
    if not parts:
        return None, None

    if len(parts) == 1:
        return parts[0], None

    return parts[0], parts[1]


def cmd_help(_state, _rooms, _arg):
    """List the commands registered in the command-handler map."""
    return ["The supported commands are: " + ", ".join(COMMANDS)]


def cmd_move(state, rooms, arg):
    """Move the player to a known room, or explain why the move cannot happen."""
    # Check the request before changing the player's current room.
    if arg is None:
        return ["Please provide a room to go to",
                "Possible rooms are: " + ", ".join(rooms)]

    if arg not in rooms:
        return ["Not a valid room.",
                "Possible rooms are: " + ", ".join(rooms)]

    if state.current_room == arg:
        return ["You are already in " + arg]

    state.current_room = arg
    return ["Moving to " + arg]


def cmd_look(state, rooms, arg):
    """Describe the current room and indicate whether it contains an item."""
    # "look" takes no argument; show the room's description and available item.
    if arg is not None:
        return ["Too many arguments. Usage: \"look\""]

    room = rooms[state.current_room]
    lines = ["Current Room: " + room.name, room.description]
    if room.item:
        lines.append("Item here: " + room.item)
    else:
        lines.append("There are no items here.")
    return lines


def cmd_inspect(state, rooms, arg):
    """Solve the current room's item and record the resulting evidence."""
    # The requested item must match the item in the room the player is currently in.
    if arg is None:
        return ["Please provide an item to inspect. Usage: \"inspect <item>\""]

    room = rooms[state.current_room]
    if arg != room.item:
        return ["There is no item called " + arg + " here. Type \"look\" to see the items."]

    # Reuse saved transcript lines if this room was already solved.
    if room.token_name in state.transcript:
        return ["You already solved this room:"] + state.transcript[room.token_name]
    
    # Check that all required tokens are collected before solving the final gate.
    if room.token_name == "FINAL":
        missing = state.missing_tokens()
        if missing:
            return ["You still need: " + ", ".join(missing)]

    # Convert expected puzzle errors into messages instead of stopping the game.
    try:
        result = room.solve(state)
    except ValueError as error:
        return [str(error)]

    if result is None:
        return ["Nothing useful was found in " + arg]

    # Format the result for display and save it so it can be shown again later.
    tagged_lines = format_result(room.token_name, result)
    state.transcript[room.token_name] = tagged_lines

    return [f"You inspect {arg}..."] + tagged_lines


def cmd_inventory(state, rooms, arg):
    """Show collected tokens and which required tokens are still missing."""
    # An empty token dictionary means the player has not solved any rooms yet.
    if not state.tokens:
        return ["Your inventory is empty."]

    # List collected tokens, then summarize what is still needed for the final gate.
    lines = ["Tokens collected:"]
    for name, token in state.tokens.items():
        lines.append(f"  {name}: {token}")

    missing = state.missing_tokens()
    if missing:
        lines.append("Still missing: " + ", ".join(missing))
    else:
        lines.append("All tokens collected!")
    return lines


def cmd_use(state, rooms, arg):
    """Allow the gate to be used from the final room once requirements are met."""
    # Validate the item and location before forwarding the request to inspection.
    if arg is None:
        return ["Please provide an item to use. Usage: \"use <item>\""]
    if state.current_room != "final":
        return ["You can only use things in the final room."]
    if arg != "gate":
        return ["You can't use " + arg + ". Only the gate can be used here."]

    # Reuse inspection's token checks and gate-solving behavior.
    return cmd_inspect(state, rooms, rooms[state.current_room].item)
        
def cmd_hint(state, rooms, _arg):
    """Return the hint configured for the current room."""
    # Each room stores its own hint text.
    return [rooms[state.current_room].hint]

def cmd_save(state, rooms, arg):
    """Write the current room, tokens, and transcripts to a JSON save file."""
    # Require a filename with the expected extension before writing anything.
    if arg is None:
        return ["Please provide a filename. Usage: \"save <filename>.json\""]
    
    if not arg.endswith(".json"):
        return ["Invalid filename. Save files must end with .json"]
    
    # Save the parts of the game state needed to continue the game later.
    data = {
        "current_room": state.current_room,
        "tokens": state.tokens,
        "transcript":state.transcript
    }

    # Report file-system errors to the player rather than crashing the game.
    try:
        with open(arg, "w", encoding = "utf-8") as file:
            json.dump(data, file, indent=4)
        return [f"[Game] Progress saved to '{arg}'."]
    
    except OSError as error:
        return [f"[Game] Error saving the progress: {error}"]

def cmd_load(state, rooms, arg):
    """Load a save file after checking that its room exists in this game."""
    # Only offer JSON files from the current directory as save files.
    save_files = sorted(
        file.name
        for file in Path(".").glob("*.json")
        if file.is_file()
    )

    # If the player did not name a file, show available choices or explain none exist.
    if arg is None:
        if save_files:
            return ["Please provide a filename. Usage: \"load <filename>\"",
                    "Available save files: " + ", ".join(save_files)]
        return ["No .json save files found."]

    # Avoid trying to open a filename that is not in the available save list.
    if arg not in save_files:
        if save_files:
            return [
                f"[Game] Save file '{arg}' does not exist.",
                "Available save files: " + ", ".join(save_files)
            ]
        return [f"[Game] Save file '{arg}' does not exist. No .json save files found."]
    
    # Read and validate the save data before restoring the game state.
    try:
        with open(arg, "r", encoding = "utf-8") as file:
            data = json.load(file)

        if not isinstance (data, dict):
            raise ValueError("Save file must contain a JSON object.")

        room = data.get("current_room")
        tokens = data.get("tokens")
        transcript = data.get("transcript")
        
        # Reject saves pointing to a room that is not part of this game.
        if room not in rooms:
            return [f"Not a valid save file: {room} is not a valid room"]
        # Restore the room, collected tokens, and solved-room transcripts.
        state.current_room = room 
        
        state.tokens = tokens 
        state.transcript = transcript
        
        return ["[Game] Progress loaded"]
    
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return [f"[Game] Error loading the progress: {error}"]

def cmd_quit(state, rooms, arg):
    """Return a farewell; the engine handles stopping the game loop."""
    # The game engine stops its input loop after displaying this message.
    return ["[Game] Goodbye."]


# Map command names to the functions that implement them.
# The engine uses this mapping to find the handler for the player's command.
COMMANDS = {
    "help": cmd_help,
    "look": cmd_look,
    "move": cmd_move,
    "inspect": cmd_inspect,
    "use": cmd_use,
    "inventory": cmd_inventory,
    "hint": cmd_hint,
    "save": cmd_save,
    "load": cmd_load,
    "quit": cmd_quit,
}
