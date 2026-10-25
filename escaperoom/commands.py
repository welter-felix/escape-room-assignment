#all the commands of the game
#every command handler gets the same 3 arguments (state, rooms, arg) and returns a list of lines to print
#the handlers do not print themselves, the engine prints the lines
from escaperoom.transcript import format_result

import json

#splits the user input into the command and its argument, e.g. "Move VAULT" -> ("move", "vault")
def parse_command(text):
    #make lowercase to make sure there is no errors with capital letters
    parts = text.strip().lower().split(maxsplit=1)

    #empty input
    if not parts:
        return None, None

    #only a command without argument, e.g. "look"
    if len(parts) == 1:
        return parts[0], None

    return parts[0], parts[1]


def cmd_help(_state, _rooms, _arg):
    #the list of commands is built from the COMMANDS dictionary, so it is always up to date
    return ["The supported commands are: " + ", ".join(COMMANDS)]


def cmd_move(state, rooms, arg):
    #sanity checks to see if the argument is correct
    if arg is None:
        return ["Please provide a room to go to",
                "Possible rooms are: " + ", ".join(rooms)]

    #check if it is a valid room in our room dict
    if arg not in rooms:
        return ["Not a valid room.",
                "Possible rooms are: " + ", ".join(rooms)]

    if state.current_room == arg:
        return ["You are already in " + arg]

    state.current_room = arg
    return ["Moving to " + arg]


def cmd_look(state, rooms, arg):
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
    if arg is None:
        return ["Please provide an item to inspect. Usage: \"inspect <item>\""]

    room = rooms[state.current_room]
    if arg != room.item:
        return ["There is no item called " + arg + " here. Type \"look\" to see the items."]

    #check if the room has already been solved by going through the transcript
    if room.token_name in state.transcript:
        return ["You already solved this room:"] + state.transcript[room.token_name]
    
    #the final gate only opens if we have all the tokens, this also covers "use gate" since it calls cmd_inspect
    if room.token_name == "FINAL":
        missing = state.missing_tokens()
        if missing:
            return ["You still need: " + ", ".join(missing)]

    #the room solves its puzzle, stores the token in the state and returns the evidence
    #the final gate still raises a ValueError as a safety check, we catch it so the game does not crash
    try:
        result = room.solve(state)
    except ValueError as error:
        return [str(error)]

    if result is None:
        return ["Nothing useful was found in " + arg]

    #we turn the result into the tagged transcript lines and store them in the state
    #inspecting a room again replaces its old lines, so the transcript never has duplicates
    tagged_lines = format_result(room.token_name, result)
    state.transcript[room.token_name] = tagged_lines

    #the player sees the same lines that end up in the transcript
    return [f"You inspect {arg}..."] + tagged_lines


def cmd_inventory(state, rooms, arg):
    if not state.tokens:
        return ["Your inventory is empty."]

    lines = ["Tokens collected:"]
    for name, token in state.tokens.items():
        lines.append(f"  {name}: {token}")

    #show which tokens are still needed for the final gate
    missing = state.missing_tokens()
    if missing:
        lines.append("Still missing: " + ", ".join(missing))
    else:
        lines.append("All tokens collected!")
    return lines


def cmd_use(state, rooms, arg):
    #we check each problem one after the other, so the player gets a specific message
    if arg is None:
        return ["Please provide an item to use. Usage: \"use <item>\""]
    if state.current_room != "final":
        return ["You can only use things in the final room."]
    if arg != "gate":
        return ["You can't use " + arg + ". Only the gate can be used here."]

    #cmd_inspect checks if we have all the tokens before opening the gate
    return cmd_inspect(state, rooms, rooms[state.current_room].item)
        
def cmd_hint(state, rooms, _arg):
    return [rooms[state.current_room].hint]

#saves the current game state to a JSON file, overwriting it if it already exists
def cmd_save(state, rooms, arg):
    
    if arg is None:
        return ["Please provide a filename. Usage: \"save <filename>\""]
    data = {
        "current_room": state.current_room,
        "tokens": state.tokens,
        "transcript":state.transcript
    }

    try:
        with open(arg, "w", encoding = "utf-8") as file:
            json.dump(data, file, indent=4)
        return ["[Game] Progress saved"]
    
    except OSError as error:
        return [f"[Game] Error saving the progress: {error}"]

#loads the game state from a JSON file, replacing the current state with the loaded one
def cmd_load(state, rooms, arg):
    if arg is None:
        return ["Please provide a filename. Usage : \"load <filename>\""]

    try:
        with open(arg, "r", encoding = "utf-8") as file:
            data = json.load(file)

        if not isinstance (data, dict):
            raise ValueError("Save file must contain a JSON object.")

        room = data.get("current_room")
        tokens = data.get("tokens")
        transcript = data.get("transcript")
        
        if room not in rooms:
            return [f"Not a valid save file: {room} is not a valid room"]
        state.current_room = room 
        
        state.tokens = tokens 
        state.transcript = transcript
        
        return ["[Game] Progress loaded"]
    except FileNotFoundError:
        return [f"[Game] Save file '{arg}' does not exist."]
    
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return [f"[Game] Error loading the progress: {error}"]

def cmd_quit(state, rooms, arg):
    #the engine checks for "quit" itself and stops the loop after printing this
    return ["[Game] Goodbye."]


#maps each command word to its handler function
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
