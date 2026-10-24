#all the commands of the game
#every command handler gets the same 3 arguments (state, rooms, arg) and returns a list of lines to print
#the handlers do not print themselves, so the engine can print the lines and also write them to the transcript

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

    #this is for removal, only bc we dont have an introroom yet
    if state.current_room not in rooms:
        return ["Current Room: " + state.current_room,
                "There is nothing here yet. Possible rooms are: " + ", ".join(rooms)]

    room = rooms[state.current_room]
    lines = ["Current Room: " + room.name, room.description]
    if room.items:
        lines.append("Items here: " + ", ".join(room.items))
    else:
        lines.append("There are no items here.")
    return lines


def cmd_inspect(state, rooms, arg):
    if arg is None:
        return ["Please provide an item to inspect. Usage: \"inspect <item>\""]

    #get the room we are in, None if it is not a room object (e.g. "intro")
    room = rooms.get(state.current_room)
    if room is None or arg not in room.items:
        return ["There is no item called " + arg + " here. Type \"look\" to see the items."]

    #the final gate only opens if we have all the tokens, this also covers "use gate" since it calls cmd_inspect
    if room.name == "final":
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

    lines = [f"You inspect {arg}..."]
    #here we add every part of the result from the solve function
    for key, value in result.items():
        lines.append(f"{key.upper()}={value}")
    return lines


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
    return cmd_inspect(state, rooms, "final_gate.txt")
        
def cmd_hint(state, rooms, _arg):
    #get the room we are in, None if it is not a room object (e.g. "intro")
    room = rooms.get(state.current_room)
    if room is None:
        return ["Type \"move <room>\" to go to a room. Rooms: " + ", ".join(rooms)]
    return [room.hint]


def cmd_save(state, rooms, arg):
    if arg is None:
        return ["Please provide a filename. Usage: \"save <filename>\""]
    data = {
        "current_room": state.current_room,
        "tokens": state.tokens,
    }

    try:
        with open(arg, "w", encoding = "utf-8") as file:
            json.dump(data, file, indent=4)
        return ["[Game] Progress saved"]
    
    except OSError as error:
        return [f"[Game] Error saving the progress: {error}"]


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

        state.current_room = room 
        state.tokens = tokens 

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
